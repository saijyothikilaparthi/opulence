## Why

The business specializes in gift hampers (predefined and customized) with configurable hamper sizes (e.g., Small, Big) and item capacities. A dedicated hamper management system allows the admin to build, edit, and organize hamper templates and products inside hampers without hardcoding rules.

## What Changes

- **Database (`app/database.py`)**: Create `hamper_sizes`, `hampers`, and `hamper_items` tables.
- **Schemas (`app/schemas.py`)**: Add Pydantic schemas for hamper size creation, hamper creation (including items), and response models.
- **Routers (`app/routers/hampers.py`)**:
  - `GET /api/hampers`: Public list of active hampers.
  - `GET /api/hampers/{id}`: Detailed view of a hamper including its items.
  - `GET /api/hamper-sizes`: List active hamper size configurations.
  - `POST /api/admin/hamper-sizes`: Admin creation of hamper sizes.
  - `POST /api/admin/hampers`: Admin creation of hampers with product items.

## Capabilities

### New Capabilities
- `hamper-management`: Configurable hamper size definitions, hamper templates, and product composition management.

### Modified Capabilities
*(None)*

## Impact

- Database schema additions (`hamper_sizes`, `hampers`, `hamper_items`).
- FastAPI router `hampers.router` registered in `app/main.py`.
