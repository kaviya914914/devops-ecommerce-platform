from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite database (file will be created automatically)
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')
conn.commit()

@app.route('/users', methods=['GET'])
def get_users():
    # Fetch all users from the database
    cursor.execute("SELECT id, name FROM users")
    users = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    # Add a new user to the database
    data = request.get_json()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (data["name"],))
    conn.commit()
    user_id = cursor.lastrowid
    return jsonify({"id": user_id, "name": data["name"]}), 201

@app.route('/')
def home():
    # Display users in a simple webpage
    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()
    user_list = "".join([f"<li>{name}</li>" for _, name in users])
    return f"""
    <h1>Users</h1>
    <ul>{user_list}</ul>
    <form onsubmit="addUser(event)">
      <input type="text" id="username" placeholder="New user name"/>
      <button>Add User</button>
    </form>
    <script>
      async function addUser(e) {{
        e.preventDefault();
        const name = document.getElementById('username').value;
        await fetch('/users', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{name}})
        }});
        location.reload();
      }}
    </script>
    """

if __name__ == '__main__':
    # Listen on all IP addresses, port 5000 (works with Docker)
    app.run(host='0.0.0.0', port=5000)