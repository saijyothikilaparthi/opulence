import psycopg


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="gift_management",
        user="gift_app",
        password="change_this_password"
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

    conn.commit()
    cursor.close()
    conn.close()

