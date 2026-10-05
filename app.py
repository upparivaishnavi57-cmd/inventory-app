from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "inventory.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            supplier TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def stock_status(quantity, reorder_level):

    if quantity == 0:
        return "OUT OF STOCK"

    elif quantity <= reorder_level:
        return "LOW STOCK"

    else:
        return "IN STOCK"


@app.route("/")
def index():

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products,
        stock_status=stock_status
    )


@app.route("/add", methods=["POST"])
def add_product():

    name = request.form["name"]
    category = request.form["category"]
    supplier = request.form["supplier"]
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    reorder_level = int(request.form["reorder_level"])

    conn = get_db()

    conn.execute("""
        INSERT INTO products
        (name, category, supplier, price, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, category, supplier, price, quantity, reorder_level))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete_product(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ('%' + keyword + '%',)
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products,
        stock_status=stock_status
    )


@app.route("/stock/<int:id>", methods=["POST"])
def update_stock(id):

    quantity = int(request.form["quantity"])

    conn = get_db()

    conn.execute(
        "UPDATE products SET quantity=? WHERE id=?",
        (quantity, id)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000
    )