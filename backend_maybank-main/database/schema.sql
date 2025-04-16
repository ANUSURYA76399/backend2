CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    address VARCHAR(255)
);

CREATE TABLE credit_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    card_number VARCHAR(16),
    previous_balance DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card_id INTEGER,
    transaction_date DATE,
    description VARCHAR(255),
    amount DECIMAL(10,2),
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);

CREATE TABLE rewards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_card_id INTEGER,
    opening_balance INTEGER,
    earned_points INTEGER,
    redeemed_points INTEGER,
    closing_balance INTEGER,
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);