## Context

Hampers are composed of products stored in `products`. We use a data-driven model for hamper sizes and a junction table for hamper items.

## Goals / Non-Goals

**Goals:**
- Add `hamper_sizes`, `hampers`, and `hamper_items` tables in `app/database.py`.
- Add Pydantic validation schemas in `app/schemas.py`.
- Implement `app/routers/hampers.py` and register it in `app/main.py`.

## Decisions

- **Junction Table**: `hamper_items` links `hamper_id` and `product_id` with a `quantity` column.
- **Relational Constraints**: Foreign key constraints cascade or set null on deletion.
