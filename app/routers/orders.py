from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import OrderCreate

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", status_code=status.HTTP_200_OK)
def list_orders():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, source, enquiry_id, category_type, customer_name, phone, email,
                   company_name, event, occasion, quantity, amount, amount_paid,
                   status, payment_status, details, notes, created_at
            FROM orders
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        orders = []
        for r in rows:
            amount = float(r[11]) if r[11] is not None else 0.0
            amount_paid = float(r[12]) if r[12] is not None else 0.0
            if amount > 0:
                paid_percent = round((amount_paid / amount) * 100, 2)
                remaining_percent = round(max(0, 100 - paid_percent), 2)
            else:
                paid_percent = 0.0
                remaining_percent = 0.0
            orders.append({
                "id": r[0],
                "source": r[1],
                "enquiry_id": r[2],
                "category_type": r[3],
                "customer_name": r[4],
                "phone": r[5],
                "email": r[6],
                "company_name": r[7],
                "event": r[8],
                "occasion": r[9],
                "quantity": r[10],
                "amount": amount,
                "amount_paid": amount_paid,
                "paid_percent": paid_percent,
                "remaining_percent": remaining_percent,
                "status": r[13],
                "payment_status": r[14] if r[14] else 'unpaid',
                "details": r[15],
                "notes": r[16],
                "created_at": r[17].isoformat() if r[17] is not None else None,
                # backward compatibility
                "event_type": r[8] or r[9],
                "total_amount": amount,
                "order_status": r[13],
            })
        return {"success": True, "data": orders}
    finally:
        cursor.close()
        connection.close()


@router.post("/admin", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        amount = order.amount if order.amount is not None else 0.0
        amount_paid = order.amount_paid if order.amount_paid is not None else 0.0
        if amount_paid >= amount and amount > 0:
            payment_status = "paid"
        elif amount_paid > 0 and amount_paid < amount:
            payment_status = "partial"
        elif order.payment_status:
            payment_status = order.payment_status
        else:
            payment_status = "unpaid"

        cursor.execute(
            """
            INSERT INTO orders (
                source, enquiry_id, category_type, customer_name, phone, email,
                company_name, event, occasion, quantity, amount, amount_paid,
                status, payment_status, details, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, customer_name, status, payment_status
            """,
            (
                order.source or "offline",
                order.enquiry_id,
                order.category_type,
                order.customer_name,
                order.phone,
                order.email,
                order.company_name,
                order.event,
                order.occasion,
                order.quantity or 1,
                amount,
                amount_paid,
                order.status or "pending",
                payment_status,
                order.details,
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


@router.post("/from-enquiry/{enquiry_id}", status_code=status.HTTP_201_CREATED)
def create_order_from_enquiry(enquiry_id: int, payload: dict = None):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT id, enquiry_type, name, phone, email, company_name,
                   occasion, quantity, budget, required_date, theme,
                   customization_details, personalize_hamper, file_url, status
            FROM enquiries WHERE id = %s
        """, (enquiry_id,))
        e = cursor.fetchone()
        if not e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")

        details_parts = []
        if e[11]:
            details_parts.append(f"Customization: {e[11]}")
        if e[12]:
            details_parts.append(f"Personalize Hamper: {e[12]}")
        if e[9]:
            details_parts.append(f"Required Date: {e[9]}")
        if e[10]:
            details_parts.append(f"Theme: {e[10]}")
        if e[13]:
            details_parts.append(f"References: {e[13]}")
        details = " | ".join(details_parts) if details_parts else None

        cursor.execute(
            """
            INSERT INTO orders (
                source, enquiry_id, category_type, customer_name, phone, email,
                company_name, event, occasion, quantity, amount, amount_paid,
                status, payment_status, details, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                "website",
                enquiry_id,
                e[1],
                e[2],
                e[3],
                e[4],
                e[5] or "N/A",
                e[6],
                e[6],
                e[7] or 1,
                float(e[8]) if e[8] is not None else 0.0,
                0.0,
                "pending",
                "unpaid",
                details,
                None
            )
        )
        row = cursor.fetchone()
        connection.commit()
        return {"success": True, "message": "Order created from enquiry", "data": {"order_id": row[0]}}
    except HTTPException:
        raise
    except Exception as ex:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create order from enquiry: {str(ex)}")
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{order_id}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_id: int, status_payload: dict):
    new_status = status_payload.get("status")
    new_payment_status = status_payload.get("payment_status")
    amount_paid = status_payload.get("amount_paid")
    amount = status_payload.get("amount")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        # Get current values
        cursor.execute("SELECT amount, amount_paid FROM orders WHERE id = %s", (order_id,))
        cur = cursor.fetchone()
        if not cur:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        cur_amount = float(cur[0]) if cur[0] is not None else 0.0
        cur_amount_paid = float(cur[1]) if cur[1] is not None else 0.0

        if amount is not None:
            cur_amount = float(amount)
        if amount_paid is not None:
            cur_amount_paid = float(amount_paid)

        # Compute payment status
        if cur_amount_paid >= cur_amount and cur_amount > 0:
            computed_payment = "paid"
        elif cur_amount_paid > 0 and cur_amount_paid < cur_amount:
            computed_payment = "partial"
        elif cur_amount_paid == 0:
            computed_payment = "unpaid"
        else:
            computed_payment = cur_payment if False else ("paid" if cur_amount_paid >= cur_amount and cur_amount > 0 else ("partial" if cur_amount_paid > 0 else "unpaid"))

        if new_payment_status:
            computed_payment = new_payment_status

        updates = []
        params = []
        if new_status is not None:
            updates.append("status = %s")
            params.append(new_status)
        updates.append("amount_paid = %s")
        params.append(cur_amount_paid)
        if amount is not None:
            updates.append("amount = %s")
            params.append(cur_amount)
        updates.append("payment_status = %s")
        params.append(computed_payment)

        params.append(order_id)
        cursor.execute(f"UPDATE orders SET {', '.join(updates)} WHERE id = %s", tuple(params))
        connection.commit()
        return {"success": True, "message": "Order updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update order: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@router.put("/admin/{order_id}/payment", status_code=status.HTTP_200_OK)
def update_order_payment(order_id: int, payment_payload: dict):
    amount_paid = payment_payload.get("amount_paid")
    amount = payment_payload.get("amount")

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT amount, amount_paid FROM orders WHERE id = %s", (order_id,))
        cur = cursor.fetchone()
        if not cur:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        cur_amount = float(cur[0]) if cur[0] is not None else 0.0
        cur_amount_paid = float(cur[1]) if cur[1] is not None else 0.0

        if amount is not None:
            cur_amount = float(amount)
        if amount_paid is not None:
            cur_amount_paid = float(amount_paid)

        if cur_amount_paid >= cur_amount and cur_amount > 0:
            payment_status = "paid"
        elif cur_amount_paid > 0 and cur_amount_paid < cur_amount:
            payment_status = "partial"
        elif cur_amount_paid == 0:
            payment_status = "unpaid"
        else:
            payment_status = "paid" if cur_amount_paid >= cur_amount and cur_amount > 0 else "partial"

        cursor.execute(
            "UPDATE orders SET amount = %s, amount_paid = %s, payment_status = %s WHERE id = %s",
            (cur_amount, cur_amount_paid, payment_status, order_id)
        )
        connection.commit()
        return {"success": True, "message": "Payment updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to update payment: {str(e)}")
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
