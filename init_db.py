import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL not set!")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            UNIQUE(user_id, project_id)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created.")

if __name__ == "__main__":
    init_db()
