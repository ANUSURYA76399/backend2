import sqlite3
import os
from datetime import datetime, timedelta

def init_database():
    try:
        # Ensure database directory exists
        if not os.path.exists('database'):
            os.makedirs('database')

        print("Initializing database...")
        conn = sqlite3.connect('database/credit_card.db')
        cursor = conn.cursor()

        # Create tables
        print("Creating tables...")
        with open('database/schema.sql', 'r') as schema_file:
            cursor.executescript(schema_file.read())

        print("Inserting sample data...")
        # Insert sample data
        cursor.execute("""
            INSERT INTO customers (name, address) 
            VALUES (?, ?)
        """, ('Ahmad Bin Ali', '123 Jalan Taman, 50100 Kuala Lumpur'))

        cursor.execute("""
            INSERT INTO credit_cards (customer_id, card_number, previous_balance) 
            VALUES (?, ?, ?)
        """, (1, '5123456789012345', 2000.00))

        # Sample transactions
        transactions = [
            (1, '2024-03-02', 'Tesco KL - Groceries', 160.00),
            (1, '2024-03-13', 'GrabPay Reload', 100.00),
            (1, '2024-03-15', 'Payment Received - FPX Transfer', -500.00),
            (1, '2024-03-25', 'Cash Advance', 200.00)
        ]
        
        cursor.executemany("""
            INSERT INTO transactions (credit_card_id, transaction_date, description, amount)
            VALUES (?, ?, ?, ?)
        """, transactions)

        # Insert rewards data
        cursor.execute("""
            INSERT INTO rewards (credit_card_id, opening_balance, earned_points, 
                               redeemed_points, closing_balance)
            VALUES (?, ?, ?, ?, ?)
        """, (1, 1200, 150, 0, 1350))

        conn.commit()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"Error occurred during database initialization: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_database()