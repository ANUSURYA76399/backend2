from statement_generator import CreditCardStatement
import os
import sqlite3

def insert_sample_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.executescript('''
            INSERT OR IGNORE INTO customers (id, name, address, email, zip_code)
            VALUES 
                (1, 'John Smith', '123 Main Street, City', 'john@email.com', '12345');
                
            INSERT OR IGNORE INTO credit_cards (id, customer_id, card_number, previous_balance, credit_limit, rewards_points)
            VALUES 
                (1, 1, '4111111111111111', 1500.00, 5000.00, 1000);
                
            INSERT OR IGNORE INTO transactions (credit_card_id, amount, date, description, transaction_type)
            VALUES 
                (1, 120.50, '2023-11-01', 'Grocery Store Purchase', 'PURCHASE'),
                (1, 500.00, '2023-11-05', 'Monthly Payment', 'PAYMENT'),
                (1, 75.25, '2023-11-10', 'Restaurant Dinner', 'PURCHASE'),
                (1, 200.00, '2023-11-15', 'Cash Withdrawal', 'CASH_ADVANCE'),
                (1, 25.00, '2023-11-20', 'Late Payment Fee', 'FINANCE_CHARGE');
        ''')
        conn.commit()
        print("Sample data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    # Ensure output directory exists
    os.makedirs('statements', exist_ok=True)
    db_path = 'database/credit_card.db'

    # Insert sample data
    insert_sample_data(db_path)

    # Initialize statement generator
    statement_gen = CreditCardStatement(db_path)

    try:
        # Generate statement for customer 1 with their credit card
        output_path = 'statements/customer_statement.pdf'
        result = statement_gen.generate_statement_pdf(
            customer_id=1,
            credit_card_id=1,
            output_path=output_path
        )
        
        if result:
            print(f"Statement generated successfully!")
            print(f"Output file: {os.path.abspath(output_path)}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()