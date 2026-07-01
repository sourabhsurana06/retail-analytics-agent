import sqlite3
import random
from datetime import datetime, timedelta


import os
print(os.getcwd())


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail.db")

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

get_connection()

def create_tables(conn):
    cursor = conn.cursor()

    cursor.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id     INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            city            TEXT NOT NULL,
            segment         TEXT NOT NULL  -- 'Premium', 'Standard', 'Budget'
        );

        CREATE TABLE products (
            product_id      INTEGER PRIMARY KEY,
            name            TEXT NOT NULL,
            category        TEXT NOT NULL,
            unit_price      REAL NOT NULL
        );

        CREATE TABLE orders (
            order_id        INTEGER PRIMARY KEY,
            customer_id     INTEGER NOT NULL REFERENCES customers(customer_id),
            order_date      TEXT NOT NULL,   -- stored as YYYY-MM-DD
            status          TEXT NOT NULL    -- 'Completed', 'Returned', 'Pending'
        );

        CREATE TABLE order_items (
            item_id         INTEGER PRIMARY KEY,
            order_id        INTEGER NOT NULL REFERENCES orders(order_id),
            product_id      INTEGER NOT NULL REFERENCES products(product_id),
            quantity        INTEGER NOT NULL,
            discount_pct    REAL NOT NULL DEFAULT 0.0   -- e.g. 0.10 = 10% off
        );
    """)
    conn.commit()

def seed_customers(conn):
    customers = [
        (1,  "Arjun Mehta",       "Mumbai",    "Premium"),
        (2,  "Priya Sharma",      "Delhi",     "Standard"),
        (3,  "Ravi Nair",         "Bangalore", "Budget"),
        (4,  "Sunita Rao",        "Chennai",   "Premium"),
        (5,  "Vikram Singh",      "Hyderabad", "Standard"),
        (6,  "Neha Gupta",        "Mumbai",    "Budget"),
        (7,  "Amit Joshi",        "Pune",      "Premium"),
        (8,  "Kavya Reddy",       "Bangalore", "Standard"),
        (9,  "Deepak Patel",      "Ahmedabad", "Budget"),
        (10, "Ananya Iyer",       "Chennai",   "Premium"),
        (11, "Rohit Verma",       "Delhi",     "Standard"),
        (12, "Meera Krishnan",    "Bangalore", "Premium"),
        (13, "Suresh Pillai",     "Kochi",     "Budget"),
        (14, "Pooja Agarwal",     "Jaipur",    "Standard"),
        (15, "Kiran Bhat",        "Bangalore", "Premium"),
    ]
    conn.executemany(
        "INSERT INTO customers VALUES (?,?,?,?)", customers
    )
    conn.commit()

def seed_products(conn):
    products = [
        (1,  "Running Shoes",      "Footwear",      2499.0),
        (2,  "Casual T-Shirt",     "Apparel",        799.0),
        (3,  "Denim Jeans",        "Apparel",       1899.0),
        (4,  "Leather Wallet",     "Accessories",    999.0),
        (5,  "Sunglasses",         "Accessories",   1499.0),
        (6,  "Backpack",           "Bags",          2199.0),
        (7,  "Sports Watch",       "Electronics",   4999.0),
        (8,  "Wireless Earbuds",   "Electronics",   3499.0),
        (9,  "Yoga Mat",           "Fitness",        899.0),
        (10, "Protein Powder",     "Fitness",       1599.0),
        (11, "Formal Shirt",       "Apparel",       1299.0),
        (12, "Tote Bag",           "Bags",           699.0),
        (13, "Perfume",            "Beauty",        2799.0),
        (14, "Face Wash",          "Beauty",         349.0),
        (15, "Notebook Set",       "Stationery",     299.0),
    ]
    conn.executemany(
        "INSERT INTO products VALUES (?,?,?,?)", products
    )
    conn.commit()   

def seed_orders_and_items(conn):
    random.seed(42)  # reproducible data

    statuses   = ["Completed", "Completed", "Completed", "Returned", "Pending"]
    start_date = datetime(2024, 1, 1)

    order_id = 1
    item_id  = 1
    orders   = []
    items    = []

    for customer_id in range(1, 16):          # 15 customers
        num_orders = random.randint(3, 8)     # 3–8 orders per customer
        for _ in range(num_orders):
            days_offset = random.randint(0, 364)
            order_date  = (start_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            status      = random.choice(statuses)
            orders.append((order_id, customer_id, order_date, status))

            num_items = random.randint(1, 4)  # 1–4 line items per order
            chosen_products = random.sample(range(1, 16), num_items)
            for product_id in chosen_products:
                quantity     = random.randint(1, 3)
                discount_pct = random.choice([0.0, 0.0, 0.05, 0.10, 0.15, 0.20])
                items.append((item_id, order_id, product_id, quantity, discount_pct))
                item_id += 1

            order_id += 1

    conn.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)
    conn.commit()
    return order_id - 1, item_id - 1   # return counts for logging

def build_database():
    conn = create_tables_and_seed()
    conn.close()

def create_tables_and_seed():
    conn = get_connection()
    print("Creating tables...")
    create_tables(conn)
    print("Seeding customers...")
    seed_customers(conn)
    print("Seeding products...")
    seed_products(conn)
    print("Seeding orders and items...")
    num_orders, num_items = seed_orders_and_items(conn)
    print(f"Done. {num_orders} orders, {num_items} line items created.")
    return conn

# ── Quick sanity-check queries ──────────────────────────────────────────────
def run_sanity_checks(conn):
    cursor = conn.cursor()

    print("\n--- Table row counts ---")
    for table in ["customers", "products", "orders", "order_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cursor.fetchone()[0]} rows")

    print("\n--- Revenue by category (Completed orders only) ---")
    cursor.execute("""
        SELECT
            p.category,
            ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount_pct)), 2) AS revenue
        FROM order_items oi
        JOIN products  p  ON p.product_id  = oi.product_id
        JOIN orders    o  ON o.order_id    = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.category
        ORDER BY revenue DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['category']}: ₹{row['revenue']:,.2f}")

    print("\n--- Top 5 customers by revenue ---")
    cursor.execute("""
        SELECT
            c.name,
            c.segment,
            ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount_pct)), 2) AS revenue
        FROM order_items oi
        JOIN products  p  ON p.product_id  = oi.product_id
        JOIN orders    o  ON o.order_id    = oi.order_id
        JOIN customers c  ON c.customer_id = o.customer_id
        WHERE o.status = 'Completed'
        GROUP BY c.customer_id
        ORDER BY revenue DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row['name']} ({row['segment']}): ₹{row['revenue']:,.2f}")

    print("\n--- Return rate by segment ---")
    cursor.execute("""
        SELECT
            c.customer_id,
            COUNT(CASE WHEN o.status = 'Returned' THEN 1 END) AS returns,
            COUNT(*) AS total_orders,
            ROUND(100.0 * COUNT(CASE WHEN o.status = 'Returned' THEN 1 END) / COUNT(*), 1) AS return_rate_pct
        FROM orders    o
        JOIN customers c ON c.customer_id = o.customer_id
        GROUP BY c.segment
        ORDER BY return_rate_pct DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row['customer_id']}: {row['return_rate_pct']}% ({row['returns']}/{row['total_orders']} orders)")

if __name__ == "__main__":
    conn = create_tables_and_seed()
    run_sanity_checks(conn)
    conn.close()


#    conn.close()