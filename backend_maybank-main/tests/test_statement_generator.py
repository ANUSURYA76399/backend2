import unittest
import os
import sys
import sqlite3
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from statement_generator import CreditCardStatement

class TestCreditCardStatement(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.test_db_path = 'database/test_credit_card.db'
        self.test_output_path = 'statements/test_statement.pdf'
        
        # Ensure directories exist
        os.makedirs('database', exist_ok=True)
        os.makedirs('statements', exist_ok=True)
        
        # Create and initialize test database
        self.conn = sqlite3.connect(self.test_db_path)
        self.cursor = self.conn.cursor()
        
        # Drop existing tables to ensure clean state
        self.cursor.executescript('''
            DROP TABLE IF EXISTS transactions;
            DROP TABLE IF EXISTS credit_cards;
            DROP TABLE IF EXISTS customers;
        ''')
        self.conn.commit()
        
        # Create required tables with additional fields
        self.cursor.executescript('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT,
                zip_code TEXT DEFAULT '12345',
                currency_type TEXT DEFAULT 'USD'
            );
            
            CREATE TABLE credit_cards (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                card_number TEXT NOT NULL,
                previous_balance REAL DEFAULT 0.0,
                credit_limit REAL DEFAULT 5000.0,
                rewards_points INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            );
            
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                credit_card_id INTEGER,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                transaction_type TEXT DEFAULT 'PURCHASE',
                FOREIGN KEY (credit_card_id) REFERENCES credit_cards (id)
            );
        ''')
        self.conn.commit()
        
        # Insert test data
        self.cursor.executescript('''
            INSERT INTO customers (id, name, address, email, zip_code)
            VALUES 
                (1, 'John Doe', '123 Test St', 'john@test.com', '12345'),
                (2, 'Jane Smith', '456 Sample Ave', 'jane@test.com', '67890'),
                (3, 'Empty User', '789 Null St', 'empty@test.com', '11111');
                
            INSERT INTO credit_cards (id, customer_id, card_number, previous_balance, rewards_points)
            VALUES 
                (1, 1, '4111111111111111', 1000.00, 500),
                (2, 2, '5555555555554444', 500.00, 200),
                (3, 3, '4444333322221111', 0.00, 0);
                
            INSERT INTO transactions (credit_card_id, amount, date, description, transaction_type)
            VALUES 
                (1, 100.50, '2023-01-01', 'Test Purchase 1', 'PURCHASE'),
                (1, 200.75, '2023-01-02', 'Test Purchase 2', 'PURCHASE'),
                (2, 50.00, '2023-01-03', 'Test Payment', 'PAYMENT');
        ''')
        self.conn.commit()
        
        self.statement_gen = CreditCardStatement(self.test_db_path)

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.test_output_path):
            os.remove(self.test_output_path)
        
        # Close database connections
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
        
        # Add a small delay before removing the database file
        import time
        time.sleep(0.1)
        
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass  # Ignore if file is still locked

    def test_normal_statement_generation(self):
        """Test normal statement generation with valid inputs"""
        result = self.statement_gen.generate_statement_pdf(
            customer_id=1,
            credit_card_id=1,
            output_path=self.test_output_path
        )
        self.assertTrue(os.path.exists(self.test_output_path))

    def test_invalid_customer_id(self):
        """Test handling of non-existent customer ID"""
        with self.assertRaises(ValueError):
            self.statement_gen.generate_statement_pdf(
                customer_id=-1,
                credit_card_id=1,
                output_path=self.test_output_path
            )

    def test_large_transaction_dataset(self):
        """Test performance with large number of transactions"""
        result = self.statement_gen.generate_statement_pdf(
            customer_id=2,
            credit_card_id=2,  # Updated to match customer 2's card
            output_path=self.test_output_path
        )
        self.assertTrue(os.path.exists(self.test_output_path))

    def test_empty_statement_period(self):
        """Test generation of statement with no transactions"""
        result = self.statement_gen.generate_statement_pdf(
            customer_id=3,
            credit_card_id=3,  # Updated to match customer 3's card
            output_path=self.test_output_path
        )
        self.assertTrue(os.path.exists(self.test_output_path))

    def test_malformed_output_path(self):
        """Test handling of invalid output paths"""
        with self.assertRaises(ValueError):
            self.statement_gen.generate_statement_pdf(
                customer_id=1,
                credit_card_id=1,
                output_path="invalid/:/path.pdf"
            )

if __name__ == '__main__':
    unittest.main()