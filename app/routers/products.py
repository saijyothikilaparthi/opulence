from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.database import get_connection
from app.schemas import ProductCreate

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", status_code=status.HTTP_200_OK)
def list_products(category_id: Optional[int] = Query(None)):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        if category_id is not None:
            cursor.execute(
                """
                SELECT id, category_id, name, description, price, image_url, is_active
                FROM products
                WHERE is_active = TRUE AND category_id = %s
                ORDER BY created_at DESC
                """,
                (category_id,)
            )
        else:
            cursor.execute(
                """
                SELECT id, category_id, name, description, price, image_url, is_active
                FROM products
                WHERE is_active = TRUE
                ORDER BY created_at DESC
                """
            )

        rows = cursor.fetchall()
        products = [
            {
                "id": r[0],
                "category_id": r[1],
                "name": r[2],
                "description": r[3],
                "price": float(r[4]) if r[4] is not None else None,
                "image_url": r[5],
                "is_active": r[6]
            }
            for r in rows
        ]
        return {"success": True, "data": products}
    finally:
        cursor.close()
        connection.close()


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
def get_product(product_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT id, category_id, name, description, price, image_url, is_active
            FROM products
            WHERE id = %s AND is_active = TRUE
            """,
            (product_id,)
        )
        r = cursor.fetchone()
        if not r:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return {
            "success": True,
            "data": {
                "id": r[0],
                "category_id": r[1],
                "name": r[2],
                "description": r[3],
                "price": float(r[4]) if r[4] is not None else None,
                "image_url": r[5],
                "is_active": r[6]
            }
        }
    finally:
        cursor.close()
        connection.close()


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO products (category_id, name, description, price, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, price
            """,
            (product.category_id, product.name, product.description, product.price, product.image_url)
        )
        row = cursor.fetchone()
        connection.commit()

        return {
            "success": True,
            "message": "Product created successfully",
            "data": {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]) if row[2] is not None else None
            }
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create product: {str(e)}"
        )
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{product_id}", status_code=status.HTTP_200_OK)
def update_product(product_id: int, product: ProductCreate):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE products
            SET category_id = %s, name = %s, description = %s, price = %s, image_url = %s
            WHERE id = %s
            RETURNING id, name, price
            """,
            (product.category_id, product.name, product.description, product.price, product.image_url, product_id)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        connection.commit()

        return {
            "success": True,
            "message": "Product updated successfully",
            "data": {"id": row[0], "name": row[1], "price": float(row[2]) if row[2] is not None else None}
        }
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update product: {str(e)}")
    finally:
        cursor.close()
        connection.close()
