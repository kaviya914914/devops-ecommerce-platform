from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite database and create table if it doesn't exist
conn = sqlite3.connect('orders.db', check_same_thread=False)
cursor = conn.cursor()

# Create table on startup
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL
)
''')
conn.commit()

# GET all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    cursor.execute("SELECT id, user_id, product_id FROM orders")
    orders = [{"id": row[0], "user_id": row[1], "product_id": row[2]} for row in cursor.fetchall()]
    return jsonify(orders)

# POST new order
@app.route('/orders', methods=['POST'])
def add_order():
    try:
        data = request.get_json()
        user_id = int(data["user_id"])
        product_id = int(data["product_id"])
        cursor.execute("INSERT INTO orders (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        conn.commit()
        order_id = cursor.lastrowid
        return jsonify({"id": order_id, "user_id": user_id, "product_id": product_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Homepage to view/add orders
@app.route('/')
def home():
    cursor.execute("SELECT id, user_id, product_id FROM orders")
    orders = cursor.fetchall()
    order_list = "".join([f"<li>Order {id}: User {user_id} ordered Product {product_id}</li>"
                          for id, user_id, product_id in orders])
    return f"""
    <h1>Orders</h1>
    <ul>{order_list}</ul>
    <form onsubmit="addOrder(event)">
      <input type="number" id="userId" placeholder="User ID" required/>
      <input type="number" id="productId" placeholder="Product ID" required/>
      <button>Add Order</button>
    </form>
    <script>
      async function addOrder(e) {{
        e.preventDefault();
        const user_id = parseInt(document.getElementById('userId').value);
        const product_id = parseInt(document.getElementById('productId').value);
        const response = await fetch('/orders', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{user_id, product_id}})
        }});
        if(response.ok) {{
          location.reload();
        }} else {{
          const err = await response.json();
          alert('Error: ' + err.error);
        }}
      }}
    </script>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)