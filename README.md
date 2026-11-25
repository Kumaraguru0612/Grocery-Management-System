# FreshMart — Grocery Management System

A beginner-friendly DBMS mini-project built with **MySQL**, **Python Flask**, and **Bootstrap 5**. It demonstrates relational database design, CRUD, foreign keys, stock updates, transactions, joins, aggregates, and views.

## Features
- Dashboard with product, category, supplier and stock counts.
- Add and view products, categories and suppliers; archive products without deleting historical references.
- Record purchases (stock increases) and sales (stock decreases).
- Sale processing uses a database transaction and row lock; a sale is rejected when stock is insufficient.
- Low-stock report based on each product's reorder level.
- SQL examples for joins, aggregate functions, views and transactions.

## Tech stack
- Python 3.10+
- Flask
- MySQL 8+
- PyMySQL
- HTML, CSS, Bootstrap 5

## 1. Create the database
Start MySQL Server, then run these scripts in MySQL Workbench in this order:

1. `database/schema.sql`
2. `database/seed.sql`

Or from a terminal (replace `YOUR_PASSWORD`):
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p grocery_db < database/seed.sql
```

## 2. Configure Python
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update your MySQL credentials. Alternatively set environment variables `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`. `config.py` automatically loads the `.env` file. You can also export the variables in your shell.

## 3. Run
```bash
python app.py
```
Open **http://127.0.0.1:5000**.

## Demo walkthrough
1. Dashboard: verify the seeded counts and low-stock alert for Banana.
2. Products: add a product, then archive it to see safe soft-delete behavior.
3. Categories and Suppliers: add records and verify they appear in their lists.
4. Purchases: select a product and add quantity; return to Products and verify stock increased.
5. Sales: sell a quantity; verify stock decreased and the bill appears in Sales.
6. Try selling more than available stock: the operation should be rejected and stock must remain unchanged.
7. Reports: review low-stock products and daily sales totals.

For GitHub screenshots, capture the Dashboard, Products, Sales, and Reports pages after running the app. Store them in a `screenshots/` folder and embed them here if desired.

## Database design (normalization)
- `categories` stores category details once; `products.category_id` references it.
- `suppliers` stores supplier details once; `products.supplier_id` is optional.
- `products` stores current stock and selling price.
- `purchases` records stock-in events.
- `sales` stores one bill header; `sale_items` stores its product line items.
- Primary keys identify each row; foreign keys preserve referential integrity. The sale header/line split avoids repeating bill-level data for every product.

## Important SQL concepts
Run `database/queries.sql` to see:
- INNER and LEFT JOINs across product/category/supplier.
- `SUM`, `COUNT`, `GROUP BY`, and sorting for inventory and sales reports.
- `v_low_stock` and `v_daily_sales` views.
- A `START TRANSACTION` / `COMMIT` example with row locking.

## Project structure
```text
grocery_management_system/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── queries.sql
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── products.html
│   ├── categories.html
│   ├── suppliers.html
│   ├── purchases.html
│   ├── sales.html
│   └── reports.html
└── static/
    └── style.css
```

## GitHub upload
Create an empty repository on GitHub, then run these commands from this project folder:
```bash
git init
git add .
git commit -m "Initial commit: Grocery Management System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/grocery-management-system.git
git push -u origin main
```
If `origin` already exists, use `git remote set-url origin https://github.com/YOUR_USERNAME/grocery-management-system.git` instead of `git remote add origin ...`.

## Notes / limitations
- This is a learning/demo application, not production POS software. Add authentication, CSRF protection, input audit logs, backups, and deployment hardening before real use.
- MySQL must be running locally. The project cannot connect until you configure valid MySQL credentials and import the schema.
- Bootstrap is loaded from jsDelivr, so an internet connection is needed for the styling CDN.
