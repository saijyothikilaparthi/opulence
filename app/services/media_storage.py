"""Storage helpers for images and user-uploaded files.

When ``SUPABASE_URL`` and ``SUPABASE_SERVICE_KEY`` are set, uploads are stored
in a public Supabase Storage bucket and only the resulting public URL is saved
in the database. This keeps files durable on hosts with an ephemeral disk
(e.g. Render free tier) and keeps binary data out of Postgres.

When those variables are not set, uploads fall back to the local ``uploads/``
folder so local development keeps working without any configuration.

To move to another S3-compatible provider later (e.g. Cloudflare R2), only the
``_upload_object`` / ``_delete_object`` helpers in this module need changing.

Environment variables:
    SUPABASE_URL             https://<project-ref>.supabase.co
    SUPABASE_SERVICE_KEY     service_role key (server-side only)
    SUPABASE_STORAGE_BUCKET  bucket name (default: media)
    IMAGE_MAX_DIMENSION      longest side in pixels after resize (default 1600)
    IMAGE_WEBP_QUALITY       WebP quality 1-100 (default 82)
"""

import io
import logging
import mimetypes
import os
import uuid

import requests
from PIL import Image

logger = logging.getLogger("media_storage")

STORAGE_TIMEOUT_SECONDS = 30
UPLOAD_ROOT = "uploads"
DEFAULT_BUCKET = "media"

# Raster formats Pillow can reliably re-encode as WebP. Animated GIFs, HEIC and
# PDFs are stored unchanged.
CONVERTIBLE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# The bucket is created/checked once per process, lazily on the first upload.
_bucket_verified = False


class MediaStorageError(RuntimeError):
    """Raised when an upload cannot be persisted."""


def _supabase_url() -> str:
    return (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")


def _service_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()


def _bucket() -> str:
    return (os.getenv("SUPABASE_STORAGE_BUCKET") or DEFAULT_BUCKET).strip()


def _max_dimension() -> int:
    try:
        return max(200, int(os.getenv("IMAGE_MAX_DIMENSION", "1600")))
    except ValueError:
        return 1600


def _webp_quality() -> int:
    try:
        return min(100, max(1, int(os.getenv("IMAGE_WEBP_QUALITY", "82"))))
    except ValueError:
        return 82


def remote_storage_enabled() -> bool:
    """True when Supabase Storage credentials are configured."""
    return bool(_supabase_url() and _service_key())


def _auth_headers(extra: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {_service_key()}"}
    if extra:
        headers.update(extra)
    return headers


def _public_url_prefix() -> str:
    return f"{_supabase_url()}/storage/v1/object/public/{_bucket()}/"


def _guess_content_type(extension: str, fallback: str | None = None) -> str:
    return (
        fallback
        or mimetypes.guess_type(f"file{extension}")[0]
        or "application/octet-stream"
    )


def _convert_to_webp(content: bytes, extension: str, content_type: str):
    """Resize a raster image to the configured max dimension and encode as WebP.

    Returns ``(content, extension, content_type)``. If the file is not a
    convertible image or conversion fails, the original bytes are returned.
    """
    if extension not in CONVERTIBLE_IMAGE_EXTENSIONS:
        return content, extension, content_type

    try:
        with Image.open(io.BytesIO(content)) as image:
            if getattr(image, "is_animated", False):
                return content, extension, content_type

            if image.mode in ("RGBA", "LA") or (
                image.mode == "P" and "transparency" in image.info
            ):
                image = image.convert("RGBA")
            else:
                image = image.convert("RGB")

            image.thumbnail(
                (_max_dimension(), _max_dimension()), Image.Resampling.LANCZOS
            )

            output = io.BytesIO()
            image.save(output, format="WEBP", quality=_webp_quality(), method=4)
            return output.getvalue(), ".webp", "image/webp"
    except Exception as exc:  # corrupt file, unsupported codec, ...
        logger.warning(
            "Could not convert upload (%s) to WebP, storing original: %s",
            extension,
            exc,
        )
        return content, extension, content_type


def _ensure_bucket() -> None:
    """Create the bucket as public if it is missing, or make it public."""
    global _bucket_verified
    if _bucket_verified or not remote_storage_enabled():
        return

    base = f"{_supabase_url()}/storage/v1/bucket"
    headers = _auth_headers({"Content-Type": "application/json"})
    try:
        response = requests.get(
            f"{base}/{_bucket()}", headers=headers, timeout=15
        )
        if response.status_code == 200:
            data = response.json() if response.content else {}
            if not data.get("public"):
                requests.put(
                    f"{base}/{_bucket()}",
                    headers=headers,
                    json={"public": True},
                    timeout=15,
                )
            _bucket_verified = True
            return

        # Supabase reports a missing bucket as 400 ("Bucket not found") or 404,
        # depending on the API version, so create it whenever the lookup fails.
        create = requests.post(
            base,
            headers=headers,
            json={"id": _bucket(), "name": _bucket(), "public": True},
            timeout=15,
        )
        if create.status_code in (200, 201):
            logger.info("Created public Supabase Storage bucket '%s'", _bucket())
            _bucket_verified = True
        elif create.status_code == 400 and "already exists" in create.text.lower():
            _bucket_verified = True
        else:
            logger.warning(
                "Could not create Supabase Storage bucket '%s' (%s): %s",
                _bucket(),
                create.status_code,
                create.text[:200],
            )
    except requests.RequestException as exc:
        # Do not fail the upload here; the upload call reports the real error.
        logger.warning(
            "Could not verify Supabase Storage bucket '%s': %s", _bucket(), exc
        )


def _upload_object(object_path: str, content: bytes, content_type: str) -> None:
    url = f"{_supabase_url()}/storage/v1/object/{_bucket()}/{object_path}"
    headers = _auth_headers({"Content-Type": content_type})
    try:
        response = requests.post(
            url, headers=headers, data=content, timeout=STORAGE_TIMEOUT_SECONDS
        )
    except requests.RequestException as exc:
        raise MediaStorageError(f"Could not reach image storage: {exc}") from exc

    if response.status_code not in (200, 201):
        raise MediaStorageError(
            "Image storage rejected the upload "
            f"({response.status_code}): {response.text[:300]}"
        )


def _delete_object(object_path: str) -> bool:
    url = f"{_supabase_url()}/storage/v1/object/{_bucket()}/{object_path}"
    try:
        response = requests.delete(
            url, headers=_auth_headers(), timeout=STORAGE_TIMEOUT_SECONDS
        )
    except requests.RequestException as exc:
        logger.warning("Could not delete stored file '%s': %s", object_path, exc)
        return False

    if response.status_code in (200, 204):
        return True
    if response.status_code != 404:
        logger.warning(
            "Image storage rejected delete for '%s' (%s): %s",
            object_path,
            response.status_code,
            response.text[:200],
        )
    return False


def save_media(
    content: bytes,
    filename: str | None,
    content_type: str | None,
    folder: str,
) -> dict:
    """Persist an upload and return ``{"url": ..., "path": ...}``.

    Images are resized and converted to WebP when possible. Files are stored in
    Supabase Storage when configured, otherwise on local disk.
    """
    extension = os.path.splitext(filename or "")[1].lower()
    content_type = _guess_content_type(extension, content_type)
    content, extension, content_type = _convert_to_webp(
        content, extension, content_type
    )
    unique_name = f"{uuid.uuid4().hex}{extension}"

    if remote_storage_enabled():
        _ensure_bucket()
        object_path = f"{folder}/{unique_name}"
        _upload_object(object_path, content, content_type)
        return {"url": _public_url_prefix() + object_path, "path": object_path}

    local_dir = os.path.join(UPLOAD_ROOT, folder)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, unique_name)
    with open(local_path, "wb") as buffer:
        buffer.write(content)
    url = "/" + local_path.replace(os.sep, "/")
    return {"url": url, "path": local_path}


def delete_media(url: str | None) -> bool:
    """Delete a previously stored file from Supabase Storage or local disk.

    Accepts both new Supabase public URLs and legacy ``/uploads/...`` paths.
    Returns True when a file was removed.
    """
    value = str(url or "").strip()
    if not value:
        return False

    prefix = _public_url_prefix()
    if remote_storage_enabled() and value.startswith(prefix):
        return _delete_object(value[len(prefix):])

    if value.startswith("/" + UPLOAD_ROOT + "/"):
        local_path = value.lstrip("/")
        if os.path.isfile(local_path):
            try:
                os.remove(local_path)
                return True
            except OSError as exc:
                logger.warning("Could not delete local file '%s': %s", local_path, exc)
    return False
