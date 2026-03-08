from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect('products.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
''')
conn.commit()

@app.route('/products', methods=['GET'])
def get_products():
    cursor.execute("SELECT id, name, price FROM products")
    products = [{"id": row[0], "name": row[1], "price": row[2]} for row in cursor.fetchall()]
    return jsonify(products)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (data["name"], data["price"]))
    conn.commit()
    product_id = cursor.lastrowid
    return jsonify({"id": product_id, "name": data["name"], "price": data["price"]}), 201

@app.route('/')
def home():
    cursor.execute("SELECT id, name, price FROM products")
    products = cursor.fetchall()
    product_list = "".join([f"<li>{name} - ${price}</li>" for _, name, price in products])
    return f"""
    <h1>Products</h1>
    <ul>{product_list}</ul>
    <form onsubmit="addProduct(event)">
      <input type="text" id="productName" placeholder="Product name" required/>
      <input type="number" id="productPrice" placeholder="Price" required/>
      <button>Add Product</button>
    </form>
    <script>
      async function addProduct(e) {{
        e.preventDefault();
        const name = document.getElementById('productName').value;
        const price = parseFloat(document.getElementById('productPrice').value);
        await fetch('/products', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{name, price}})
        }});
        location.reload();
      }}
    </script>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)