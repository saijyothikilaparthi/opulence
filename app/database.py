import os

import psycopg


def get_connection():
    # Defaults match the local development setup; override via environment in production
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "gift_management"),
        user=os.getenv("DB_USER", "gift_app"),
        password=os.getenv("DB_PASSWORD", "change_this_password"),
        connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Ensure the public schema exists and is in the search path
    try:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS public;")
        conn.commit()
    except Exception:
        conn.rollback()
        
    cursor.execute("SET search_path TO public;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.enquiries (
            id SERIAL PRIMARY KEY,
            enquiry_type VARCHAR(20) NOT NULL CHECK (enquiry_type IN ('individual', 'corporate', 'customized')),
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            company_name VARCHAR(150),
            occasion VARCHAR(100),
            quantity INT,
            budget NUMERIC(10, 2),
            required_date DATE,
            theme VARCHAR(100),
            customization_details TEXT,
            personalize_hamper TEXT,
            file_url TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.orders (
            id SERIAL PRIMARY KEY,
            source VARCHAR(50) DEFAULT 'offline',
            customer_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            event VARCHAR(100),
            quantity INT DEFAULT 1,
            amount NUMERIC(10, 2),
            status VARCHAR(30) DEFAULT 'pending',
            payment_status VARCHAR(30) DEFAULT 'unpaid',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    try:
        cursor.execute("""
            ALTER TABLE public.orders ADD COLUMN IF NOT EXISTS payment_status VARCHAR(30) DEFAULT 'unpaid';
        """)
    except Exception:
        conn.rollback()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.gallery_work (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150),
            category VARCHAR(100),
            image_url TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Catalog tables used by the categories, products and hampers routers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            image_url TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.products (
            id SERIAL PRIMARY KEY,
            category_id INT REFERENCES public.categories(id) ON DELETE SET NULL,
            name VARCHAR(150) NOT NULL,
            description TEXT,
            price NUMERIC(10, 2),
            image_url TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.hamper_sizes (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            max_items INT NOT NULL CHECK (max_items >= 1),
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.hampers (
            id SERIAL PRIMARY KEY,
            size_id INT REFERENCES public.hamper_sizes(id) ON DELETE SET NULL,
            name VARCHAR(150) NOT NULL,
            description TEXT,
            price NUMERIC(10, 2),
            image_url TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS public.hamper_items (
            id SERIAL PRIMARY KEY,
            hamper_id INT NOT NULL REFERENCES public.hampers(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
            quantity INT NOT NULL DEFAULT 1 CHECK (quantity >= 1)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

