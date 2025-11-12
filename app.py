from flask import Flask, jsonify, request
import mysql.connector
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'your_super_secret_key' # CHANGE THIS TO A STRONG, RANDOM KEY IN PRODUCTION

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root', # Assuming default XAMPP/WAMP user
    'password': '', # Assuming default XAMPP/WAMP password
    'database': 'safetravel'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@app.route('/')
def home():
    return "Welcome to the Flask Backend for safetravel database!"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # You might want to fetch the user from the database here based on data['id']
            # For now, we'll just pass the user_id
            request.user_id = data['id']
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users', methods=['GET'])
@token_required
def get_current_user():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, uid, name, email, phone, avatar_url, created_at FROM users WHERE id = %s", (request.user_id,))
        user = cursor.fetchone()
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except mysql.connector.Error as err:
        print(f"Error fetching current user: {err}")
        return jsonify({"error": "Error fetching current user"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_user():
    new_user_data = request.json
    required_fields = ["uid", "name", "email", "password"] # Changed to 'password' for registration
    if not all(field in new_user_data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400
    
    hashed_password = bcrypt.generate_password_hash(new_user_data["password"]).decode('utf-8')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO users (uid, name, email, phone, password_hash, avatar_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            new_user_data["uid"],
            new_user_data["name"],
            new_user_data["email"],
            new_user_data.get("phone"),
            hashed_password, # Store hashed password
            new_user_data.get("avatar_url")
        )
        cursor.execute(query, values)
        conn.commit()
        new_user_id = cursor.lastrowid
        return jsonify({"id": new_user_id, "uid": new_user_data["uid"], "name": new_user_data["name"], "email": new_user_data["email"]}), 201
    except mysql.connector.Error as err:
        print(f"Error adding user: {err}")
        conn.rollback()
        return jsonify({"error": "Error adding user"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login_user():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (auth['email'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
        
        if bcrypt.check_password_hash(user['password_hash'], auth['password']):
            token = jwt.encode({'id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({'token': token})
        
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return jsonify({"error": "Error during login"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['GET'])
@token_required
def get_specific_user(user_id):
    if request.user_id != user_id:
        return jsonify({"error": "Unauthorized access to user data"}), 403

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, uid, name, email, phone, avatar_url, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    except mysql.connector.Error as err:
        print(f"Error fetching user: {err}")
        return jsonify({"error": "Error fetching user"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_specific_user(user_id):
    if request.user_id != user_id:
        return jsonify({"error": "Unauthorized to update this user"}), 403

    updates = request.json
    if not updates:
        return jsonify({"error": "No updates provided"}), 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        set_clauses = []
        values = []
        for key, value in updates.items():
            if key in ["uid", "name", "email", "phone", "avatar_url"]:
                set_clauses.append(f"{key} = %s")
                values.append(value)
            elif key == "password":
                hashed_password = bcrypt.generate_password_hash(value).decode('utf-8')
                set_clauses.append("password_hash = %s")
                values.append(hashed_password)
        
        if not set_clauses:
            return jsonify({"error": "No valid fields to update"}), 400

        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
        values.append(user_id)
        
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount > 0:
            cursor.execute("SELECT id, uid, name, email, phone, avatar_url, created_at FROM users WHERE id = %s", (user_id,))
            updated_user = cursor.fetchone()
            return jsonify(updated_user)
        return jsonify({"error": "User not found"}), 404
    except mysql.connector.Error as err:
        print(f"Error updating user: {err}")
        conn.rollback()
        return jsonify({"error": "Error updating user"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_specific_user(user_id):
    if request.user_id != user_id:
        return jsonify({"error": "Unauthorized to delete this user"}), 403

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({"message": "User deleted"}), 200
        return jsonify({"error": "User not found"}), 404
    except mysql.connector.Error as err:
        print(f"Error deleting user: {err}")
        conn.rollback()
        return jsonify({"error": "Error deleting user"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
