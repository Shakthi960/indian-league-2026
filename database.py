import sqlite3


def create_database():

    conn = sqlite3.connect("players.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        firstname TEXT NOT NULL,
        middlename TEXT,
        lastname TEXT NOT NULL,

        email TEXT UNIQUE,
        phone TEXT UNIQUE,

        dob TEXT,
        age INTEGER,

        state TEXT,
        sport TEXT,

        photo TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # indexes for faster queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_phone ON players(phone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_email ON players(email)")

    conn.commit()
    conn.close()

    print("Database ready")


if __name__ == "__main__":
    create_database()