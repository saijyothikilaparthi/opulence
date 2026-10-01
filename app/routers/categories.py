import re
from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import CategoryCreate

router = APIRouter(prefix="/api/categories", tags=["Categories"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)


@router.get("", status_code=status.HTTP_200_OK)
def list_categories():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, name, slug, description, image_url, is_active
            FROM categories
            WHERE is_active = TRUE
            ORDER BY name ASC
        """)
        rows = cursor.fetchall()
        categories = [
            {
                "id": r[0],
                "name": r[1],
                "slug": r[2],
                "description": r[3],
                "image_url": r[4],
                "is_active": r[5]
            }
            for r in rows
        ]
        return {"success": True, "data": categories}
    finally:
        cursor.close()
        connection.close()


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate):
    connection = get_connection()
    cursor = connection.cursor()

    slug = category.slug if category.slug else slugify(category.name)

    try:
        cursor.execute(
            """
            INSERT INTO categories (name, slug, description, image_url)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, slug
            """,
            (category.name, slug, category.description, category.image_url)
        )
        row = cursor.fetchone()
        connection.commit()

        return {
            "success": True,
            "message": "Category created successfully",
            "data": {
                "id": row[0],
                "name": row[1],
                "slug": row[2]
            }
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create category: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{category_id}", status_code=status.HTTP_200_OK)
def update_category(category_id: int, category: CategoryCreate):
    connection = get_connection()
    cursor = connection.cursor()

    slug = category.slug if category.slug else slugify(category.name)

    try:
        cursor.execute(
            """
            UPDATE categories
            SET name = %s, slug = %s, description = %s, image_url = %s
            WHERE id = %s
            RETURNING id, name, slug
            """,
            (category.name, slug, category.description, category.image_url, category_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        connection.commit()

        return {
            "success": True,
            "message": "Category updated successfully",
            "data": {"id": row[0], "name": row[1], "slug": row[2]}
        }
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update category: {str(e)}")
    finally:
        cursor.close()
        connection.close()
