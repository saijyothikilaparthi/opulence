from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import OrderCreate

router = APIRouter(prefix="/api/orders", tags=["Orders"])

ORDER_STATUSES = {"pending", "in-progress", "completed", "cancelled"}
PAYMENT_STATUSES = {"unpaid", "partial", "paid"}


@router.get("", status_code=status.HTTP_200_OK)
def list_orders():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, source, customer_name, phone, email, event, quantity, amount, status, payment_status, notes, created_at
            FROM orders
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        orders = [
            {
                "id": r[0],
                "source": r[1],
                "customer_name": r[2],
                "phone": r[3],
                "email": r[4],
                "event": r[5],
                "quantity": r[6],
                "amount": float(r[7]) if r[7] is not None else None,
                "status": r[8],
                "payment_status": r[9] if len(r) > 9 and r[9] else 'unpaid',
                "notes": r[10] if len(r) > 10 else None,
                "created_at": r[11].isoformat() if len(r) > 11 and r[11] else None
            }
            for r in rows
        ]
        return {"success": True, "data": orders}
    finally:
        cursor.close()
        connection.close()


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    if order.status not in ORDER_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{order.status}'")
    if order.payment_status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payment_status '{order.payment_status}'")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO orders (source, customer_name, phone, email, event, quantity, amount, status, payment_status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, customer_name, status, payment_status
            """,
            (
                order.source,
                order.customer_name,
                order.phone,
                order.email,
                order.event,
                order.quantity,
                order.amount,
                order.status,
                order.payment_status,
                order.notes
            )
        )
        row = cursor.fetchone()
        connection.commit()
        return {
            "success": True,
            "message": "Order created successfully",
            "data": {
                "id": row[0],
                "customer_name": row[1],
                "status": row[2],
                "payment_status": row[3]
            }
        }
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create order: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{order_id}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, status_payload: dict):
    new_status = status_payload.get("status")
    new_payment_status = status_payload.get("payment_status")

    if not new_status and not new_payment_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide status or payment_status")
    if new_status and new_status not in ORDER_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status '{new_status}'")
    if new_payment_status and new_payment_status not in PAYMENT_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payment_status '{new_payment_status}'")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE orders
            SET status = COALESCE(%s, status), payment_status = COALESCE(%s, payment_status)
            WHERE id = %s
            RETURNING id
            """,
            (new_status, new_payment_status, order_id)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        connection.commit()
        return {"success": True, "message": "Order updated successfully"}
    except HTTPException:
        connection.rollback()
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update order: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.delete("/admin/{order_id}", status_code=status.HTTP_200_OK)
def delete_order(order_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM orders WHERE id = %s RETURNING id", (order_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        connection.commit()
        return {"success": True, "message": f"Order #{order_id} deleted successfully"}
    finally:
        cursor.close()
        connection.close()
