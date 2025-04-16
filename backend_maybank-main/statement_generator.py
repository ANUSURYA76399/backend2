from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime, timedelta
import sqlite3

class CreditCardStatement:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.statement_date = datetime.now()
        self.due_date = self.statement_date + timedelta(days=21)

    def get_customer_data(self, customer_id, credit_card_id):
        customer_query = """
            SELECT 
                c.name, c.address, cc.card_number, 
                COALESCE(cc.previous_balance, 0.0) as previous_balance,
                c.zip_code, c.currency_type,
                cc.credit_limit, cc.rewards_points
            FROM customers c
            LEFT JOIN credit_cards cc ON c.id = cc.customer_id
            WHERE c.id = ? AND (cc.id = ? OR cc.id IS NULL)
        """
        result = self.cursor.execute(customer_query, (customer_id, credit_card_id)).fetchone()
        if not result:
            raise ValueError("Invalid customer ID")
        if result[2] is None:
            raise ValueError("Invalid credit card ID")
        return result

    def get_transactions_by_type(self, credit_card_id):
        query = """
            SELECT 
                amount, date, description,
                transaction_type,
                CASE 
                    WHEN transaction_type = 'PURCHASE' THEN amount
                    ELSE 0 
                END as purchase_amount,
                CASE 
                    WHEN transaction_type = 'PAYMENT' THEN amount
                    ELSE 0 
                END as payment_amount,
                CASE 
                    WHEN transaction_type = 'CASH_ADVANCE' THEN amount
                    ELSE 0 
                END as cash_advance_amount,
                CASE 
                    WHEN transaction_type = 'FINANCE_CHARGE' THEN amount
                    ELSE 0 
                END as finance_charge_amount
            FROM transactions
            WHERE credit_card_id = ?
            ORDER BY date, transaction_type
        """
        return self.cursor.execute(query, (credit_card_id,)).fetchall()

    def calculate_minimum_payment(self, new_balance):
        return max(min(new_balance * 0.02, 25.00), new_balance)

    def generate_statement_pdf(self, customer_id, credit_card_id, output_path):
        try:
            customer_data = self.get_customer_data(customer_id, credit_card_id)
            transactions = self.get_transactions_by_type(credit_card_id)
            
            c = canvas.Canvas(output_path, pagesize=letter)
            
            # Header with Logo and Statement Date
            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, 750, "Credit Card Statement")
            c.setFont("Helvetica", 10)
            c.drawString(450, 750, f"Statement Date: {self.statement_date.strftime('%Y-%m-%d')}")
            c.drawString(450, 735, f"Due Date: {self.due_date.strftime('%Y-%m-%d')}")

            # Customer Information Box
            c.rect(50, 650, 500, 70)
            c.setFont("Helvetica", 12)
            c.drawString(60, 700, f"Name: {customer_data[0]}")
            c.drawString(60, 680, f"Card Number: {'*' * 12 + customer_data[2][-4:]}")
            c.drawString(60, 660, f"Address: {customer_data[1]}, ZIP: {customer_data[4]}")

            # Account Summary Box and Title
            c.setFont("Helvetica-Bold", 12)
            c.drawString(60, 620, "Account Summary")
            c.rect(50, 540, 500, 70)  # Adjusted box position and height
            
            # Calculate totals
            totals = {'purchases': 0, 'payments': 0, 'cash_advances': 0, 'finance_charges': 0}
            for trans in transactions:
                totals['purchases'] += trans[4]
                totals['payments'] += trans[5]
                totals['cash_advances'] += trans[6]
                totals['finance_charges'] += trans[7]

            new_balance = customer_data[3] + sum(totals.values())
            min_payment = self.calculate_minimum_payment(new_balance)

            # Account Summary Details with better alignment
            c.setFont("Helvetica", 10)
            x1 = 60   # Left column x position
            x2 = 220  # Middle column x position
            x3 = 380  # Right column x position
            y_start = 580  # Adjusted starting y position
            y_step = 15

            # Format currency values
            c.drawString(x1, y_start, "Previous Balance:")
            c.drawRString(x1 + 140, y_start, f"${customer_data[3]:.2f}")
            
            c.drawString(x1, y_start - y_step, "Purchases:")
            c.drawRString(x1 + 140, y_start - y_step, f"${totals['purchases']:.2f}")
            
            c.drawString(x1, y_start - 2*y_step, "Payments:")
            c.drawRString(x1 + 140, y_start - 2*y_step, f"${totals['payments']:.2f}")

            # Middle column
            c.drawString(x2, y_start, "Cash Advances:")
            c.drawRString(x2 + 140, y_start, f"${totals['cash_advances']:.2f}")
            
            c.drawString(x2, y_start - y_step, "Finance Charges:")
            c.drawRString(x2 + 140, y_start - y_step, f"${totals['finance_charges']:.2f}")
            
            c.drawString(x2, y_start - 2*y_step, "New Balance:")
            c.drawRString(x2 + 140, y_start - 2*y_step, f"${new_balance:.2f}")

            # Right column
            c.drawString(x3, y_start, "Credit Limit:")
            c.drawRString(x3 + 140, y_start, f"${customer_data[6]:.2f}")
            
            c.drawString(x3, y_start - y_step, "Available Credit:")
            c.drawRString(x3 + 140, y_start - y_step, f"${(customer_data[6] - new_balance):.2f}")
            
            c.drawString(x3, y_start - 2*y_step, "Minimum Payment:")
            c.drawRString(x3 + 140, y_start - 2*y_step, f"${min_payment:.2f}")

            # Transactions Table
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 520, "Transaction Details")
            
            # Create transaction table data
            data = [['Date', 'Description', 'Type', 'Amount']]
            for trans in transactions:
                data.append([
                    trans[1],
                    trans[2],
                    trans[3],
                    f"${trans[0]:.2f}"
                ])

            table = Table(data, colWidths=[80, 250, 100, 70])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey)
            ]))
            
            table.wrapOn(c, 400, 400)
            table.drawOn(c, 50, 300)

            # Rewards Summary
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 250, "Rewards Summary")
            c.setFont("Helvetica", 10)
            c.drawString(50, 235, f"Available Points: {customer_data[7]}")

            c.save()
            return True
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error generating statement: {str(e)}")