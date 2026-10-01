from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import HamperSizeCreate, HamperCreate

router = APIRouter(tags=["Hampers"])


@router.get("/api/hamper-sizes", status_code=status.HTTP_200_OK)
def list_hamper_sizes():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, name, max_items, description, is_active
            FROM hamper_sizes
            WHERE is_active = TRUE
            ORDER BY max_items ASC
        """)
        rows = cursor.fetchall()
        sizes = [
            {
                "id": r[0],
                "name": r[1],
                "max_items": r[2],
                "description": r[3],
                "is_active": r[4]
            }
            for r in rows
        ]
        return {"success": True, "data": sizes}
    finally:
        cursor.close()
        connection.close()


@router.post("/api/admin/hamper-sizes", status_code=status.HTTP_201_CREATED)
def create_hamper_size(size: HamperSizeCreate):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO hamper_sizes (name, max_items, description)
            VALUES (%s, %s, %s)
            RETURNING id, name, max_items
            """,
            (size.name, size.max_items, size.description)
        )
        row = cursor.fetchone()
        connection.commit()
        return {
            "success": True,
            "message": "Hamper size created successfully",
            "data": {
                "id": row[0],
                "name": row[1],
                "max_items": row[2]
            }
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create hamper size: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()


@router.get("/api/hampers", status_code=status.HTTP_200_OK)
def list_hampers():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT h.id, h.size_id, s.name AS size_name, h.name, h.description, h.price, h.image_url, h.is_active
            FROM hampers h
            LEFT JOIN hamper_sizes s ON h.size_id = s.id
            WHERE h.is_active = TRUE
            ORDER BY h.created_at DESC
        """)
        rows = cursor.fetchall()
        hampers = [
            {
                "id": r[0],
                "size_id": r[1],
                "size_name": r[2],
                "name": r[3],
                "description": r[4],
                "price": float(r[5]) if r[5] is not None else None,
                "image_url": r[6],
                "is_active": r[7]
            }
            for r in rows
        ]
        return {"success": True, "data": hampers}
    finally:
        cursor.close()
        connection.close()


@router.get("/api/hampers/{hamper_id}", status_code=status.HTTP_200_OK)
def get_hamper(hamper_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT h.id, h.size_id, s.name AS size_name, s.max_items, h.name, h.description, h.price, h.image_url, h.is_active
            FROM hampers h
            LEFT JOIN hamper_sizes s ON h.size_id = s.id
            WHERE h.id = %s AND h.is_active = TRUE
            """,
            (hamper_id,)
        )
        h = cursor.fetchone()
        if not h:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hamper not found"
            )

        cursor.execute(
            """
            SELECT hi.product_id, p.name, p.price, hi.quantity, p.image_url
            FROM hamper_items hi
            JOIN products p ON hi.product_id = p.id
            WHERE hi.hamper_id = %s
            """,
            (hamper_id,)
        )
        items_rows = cursor.fetchall()
        items = [
            {
                "product_id": item[0],
                "product_name": item[1],
                "price": float(item[2]) if item[2] is not None else None,
                "quantity": item[3],
                "image_url": item[4]
            }
            for item in items_rows
        ]

        return {
            "success": True,
            "data": {
                "id": h[0],
                "size_id": h[1],
                "size_name": h[2],
                "max_items": h[3],
                "name": h[4],
                "description": h[5],
                "price": float(h[6]) if h[6] is not None else None,
                "image_url": h[7],
                "is_active": h[8],
                "items": items
            }
        }
    finally:
        cursor.close()
        connection.close()


@router.post("/api/admin/hampers", status_code=status.HTTP_201_CREATED)
def create_hamper(hamper: HamperCreate):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO hampers (size_id, name, description, price, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, price
            """,
            (hamper.size_id, hamper.name, hamper.description, hamper.price, hamper.image_url)
        )
        row = cursor.fetchone()
        hamper_id = row[0]

        if hamper.items:
            for item in hamper.items:
                cursor.execute(
                    """
                    INSERT INTO hamper_items (hamper_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (hamper_id, item.product_id, item.quantity)
                )

        connection.commit()

        return {
            "success": True,
            "message": "Hamper created successfully",
            "data": {
                "id": hamper_id,
                "name": row[1],
                "price": float(row[2]) if row[2] is not None else None
            }
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create hamper: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()
