import sqlite3
import os

def update_database_schema():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/credit_card.db')
    cursor = conn.cursor()

    try:
        # Create tables if they don't exist
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT,
                zip_code TEXT,
                currency_type TEXT DEFAULT 'USD'
            );
            
            CREATE TABLE IF NOT EXISTS credit_cards (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                card_number TEXT NOT NULL,
                previous_balance REAL DEFAULT 0.0,
                credit_limit REAL DEFAULT 5000.0,
                rewards_points INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            );
            
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                credit_card_id INTEGER,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                transaction_type TEXT CHECK(
                    transaction_type IN ('PURCHASE', 'PAYMENT', 'CASH_ADVANCE', 'FINANCE_CHARGE')
                ),
                FOREIGN KEY (credit_card_id) REFERENCES credit_cards (id)
            );
        ''')
        conn.commit()
        print("Database schema created/updated successfully!")
    except sqlite3.Error as e:
        print(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_database_schema()