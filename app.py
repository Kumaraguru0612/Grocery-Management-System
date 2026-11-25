from decimal import Decimal, InvalidOperation
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from pymysql.cursors import DictCursor
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

def get_db():
    return pymysql.connect(cursorclass=DictCursor, autocommit=False, **DB_CONFIG)

def query(sql, args=(), one=False):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            result = cur.fetchone() if one else cur.fetchall()
        conn.commit()
        return result
    finally:
        conn.close()

@app.route("/")
def dashboard():
    stats = query("""
        SELECT
          (SELECT COUNT(*) FROM products WHERE is_active=1) AS products,
          (SELECT COUNT(*) FROM categories) AS categories,
          (SELECT COUNT(*) FROM suppliers) AS suppliers,
          (SELECT COALESCE(SUM(quantity),0) FROM products) AS units
    """, one=True)
    low = query("""SELECT p.*, c.category_name FROM products p
                   JOIN categories c ON c.category_id=p.category_id
                   WHERE p.is_active=1 AND p.quantity <= p.reorder_level
                   ORDER BY p.quantity ASC LIMIT 8""")
    recent = query("""SELECT s.sale_id, s.sale_date, s.total_amount, s.payment_method
                      FROM sales s ORDER BY s.sale_id DESC LIMIT 5""")
    return render_template("dashboard.html", stats=stats, low=low, recent=recent)

@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        try:
            data = (request.form["name"].strip(), int(request.form["category_id"]),
                    int(request.form["supplier_id"]) or None, Decimal(request.form["price"]),
                    int(request.form["quantity"]), int(request.form["reorder_level"]))
            if not data[0] or data[3] < 0 or data[4] < 0 or data[5] < 0:
                raise ValueError()
            query("""INSERT INTO products(product_name,category_id,supplier_id,unit_price,quantity,reorder_level)
                     VALUES(%s,%s,%s,%s,%s,%s)""", data)
            flash("Product added successfully.", "success")
        except (ValueError, InvalidOperation, KeyError):
            flash("Please enter valid product details.", "danger")
        return redirect(url_for("products"))
    rows = query("""SELECT p.*, c.category_name, s.supplier_name FROM products p
                    JOIN categories c ON c.category_id=p.category_id
                    LEFT JOIN suppliers s ON s.supplier_id=p.supplier_id
                    WHERE p.is_active=1 ORDER BY p.product_name""")
    return render_template("products.html", products=rows,
                           categories=query("SELECT * FROM categories ORDER BY category_name"),
                           suppliers=query("SELECT * FROM suppliers ORDER BY supplier_name"))

@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):
    if request.method == "POST":
        try:
            values = (request.form["name"].strip(), int(request.form["category_id"]),
                      int(request.form["supplier_id"]) or None, Decimal(request.form["price"]),
                      int(request.form["reorder_level"]), product_id)
            if not values[0] or values[3] < 0 or values[4] < 0:
                raise ValueError()
            query("""UPDATE products SET product_name=%s,category_id=%s,supplier_id=%s,
                      unit_price=%s,reorder_level=%s WHERE product_id=%s""", values)
            flash("Product updated.", "success")
            return redirect(url_for("products"))
        except (ValueError, InvalidOperation, KeyError):
            flash("Please enter valid product details.", "danger")
    product = query("SELECT * FROM products WHERE product_id=%s AND is_active=1", (product_id,), one=True)
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for("products"))
    return render_template("edit_product.html", product=product,
                           categories=query("SELECT * FROM categories ORDER BY category_name"),
                           suppliers=query("SELECT * FROM suppliers ORDER BY supplier_name"))

@app.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    query("UPDATE products SET is_active=0 WHERE product_id=%s", (product_id,))
    flash("Product archived (transaction history is preserved).", "info")
    return redirect(url_for("products"))

@app.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            try:
                query("INSERT INTO categories(category_name) VALUES(%s)", (name,))
                flash("Category added.", "success")
            except pymysql.err.IntegrityError:
                flash("That category already exists.", "warning")
        return redirect(url_for("categories"))
    return render_template("categories.html", categories=query("SELECT * FROM categories ORDER BY category_name"))

@app.post("/categories/<int:category_id>/edit")
def edit_category(category_id):
    name = request.form.get("name", "").strip()
    if name:
        try:
            query("UPDATE categories SET category_name=%s WHERE category_id=%s", (name, category_id))
            flash("Category updated.", "success")
        except pymysql.err.IntegrityError:
            flash("Category name already exists or is in use.", "warning")
    return redirect(url_for("categories"))

@app.post("/categories/<int:category_id>/delete")
def delete_category(category_id):
    try:
        query("DELETE FROM categories WHERE category_id=%s", (category_id,))
        flash("Category deleted.", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete a category assigned to products.", "warning")
    return redirect(url_for("categories"))

@app.route("/suppliers", methods=["GET", "POST"])
def suppliers():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        if name:
            query("INSERT INTO suppliers(supplier_name,phone,email) VALUES(%s,%s,%s)",
                  (name, phone or None, email or None))
            flash("Supplier added.", "success")
        return redirect(url_for("suppliers"))
    return render_template("suppliers.html", suppliers=query("SELECT * FROM suppliers ORDER BY supplier_name"))

@app.post("/suppliers/<int:supplier_id>/edit")
def edit_supplier(supplier_id):
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    if name:
        query("UPDATE suppliers SET supplier_name=%s,phone=%s,email=%s WHERE supplier_id=%s",
              (name, phone or None, email or None, supplier_id))
        flash("Supplier updated.", "success")
    return redirect(url_for("suppliers"))

@app.post("/suppliers/<int:supplier_id>/delete")
def delete_supplier(supplier_id):
    try:
        query("DELETE FROM suppliers WHERE supplier_id=%s", (supplier_id,))
        flash("Supplier deleted.", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete a supplier linked to products.", "warning")
    return redirect(url_for("suppliers"))

@app.route("/purchases", methods=["GET", "POST"])
def purchases():
    if request.method == "POST":
        try:
            product_id, qty = int(request.form["product_id"]), int(request.form["quantity"])
            cost = Decimal(request.form["unit_cost"])
            if qty <= 0 or cost < 0: raise ValueError()
            conn = get_db()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT product_id FROM products WHERE product_id=%s AND is_active=1 FOR UPDATE", (product_id,))
                    if not cur.fetchone(): raise ValueError()
                    cur.execute("""INSERT INTO purchases(product_id,quantity,unit_cost,total_cost)
                                   VALUES(%s,%s,%s,%s)""", (product_id, qty, cost, qty*cost))
                    cur.execute("UPDATE products SET quantity=quantity+%s WHERE product_id=%s", (qty, product_id))
                conn.commit()
                flash("Purchase recorded and stock increased.", "success")
            except Exception:
                conn.rollback()
                raise
            finally: conn.close()
        except (ValueError, InvalidOperation, KeyError):
            flash("Invalid purchase details.", "danger")
        return redirect(url_for("purchases"))
    rows = query("""SELECT pu.*, p.product_name FROM purchases pu JOIN products p USING(product_id)
                    ORDER BY pu.purchase_id DESC LIMIT 50""")
    return render_template("purchases.html", purchases=rows,
                           products=query("SELECT product_id,product_name FROM products WHERE is_active=1 ORDER BY product_name"))

@app.route("/sales", methods=["GET", "POST"])
def sales():
    if request.method == "POST":
        try:
            product_id, qty = int(request.form["product_id"]), int(request.form["quantity"])
            payment = request.form["payment_method"]
            if qty <= 0 or payment not in ("Cash", "Card", "UPI"): raise ValueError()
            conn = get_db()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT unit_price,quantity FROM products WHERE product_id=%s AND is_active=1 FOR UPDATE", (product_id,))
                    product = cur.fetchone()
                    if not product or product["quantity"] < qty:
                        raise ValueError("Insufficient stock")
                    total = product["unit_price"] * qty
                    cur.execute("INSERT INTO sales(total_amount,payment_method) VALUES(%s,%s)", (total,payment))
                    sale_id = cur.lastrowid
                    cur.execute("""INSERT INTO sale_items(sale_id,product_id,quantity,unit_price,line_total)
                                   VALUES(%s,%s,%s,%s,%s)""",
                                (sale_id,product_id,qty,product["unit_price"],total))
                    cur.execute("UPDATE products SET quantity=quantity-%s WHERE product_id=%s", (qty,product_id))
                conn.commit()
                flash(f"Sale #{sale_id} recorded. Stock updated.", "success")
            except Exception:
                conn.rollback()
                raise
            finally: conn.close()
        except (ValueError, KeyError):
            flash("Sale could not be completed. Check stock and entered values.", "danger")
        return redirect(url_for("sales"))
    rows = query("""SELECT s.*, COUNT(si.sale_item_id) AS item_lines
                    FROM sales s LEFT JOIN sale_items si ON s.sale_id=si.sale_id
                    GROUP BY s.sale_id ORDER BY s.sale_id DESC LIMIT 50""")
    return render_template("sales.html", sales=rows,
                           products=query("SELECT product_id,product_name,unit_price,quantity FROM products WHERE is_active=1 AND quantity>0 ORDER BY product_name"))

@app.route("/reports")
def reports():
    low = query("""SELECT p.product_name,p.quantity,p.reorder_level,c.category_name
                   FROM products p JOIN categories c USING(category_id)
                   WHERE p.is_active=1 AND p.quantity<=p.reorder_level ORDER BY p.quantity""")
    totals = query("""SELECT DATE(sale_date) AS sale_day, COUNT(*) AS bills,
                      SUM(total_amount) AS revenue FROM sales
                      GROUP BY DATE(sale_date) ORDER BY sale_day DESC LIMIT 7""")
    return render_template("reports.html", low=low, totals=totals)

if __name__ == "__main__":
    app.run(debug=True)
