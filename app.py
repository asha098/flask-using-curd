from flask import Flask, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'many_random_bytes')

# MySQL Configuration (Use environment variables for security)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'new_password'  # Ensure this is correct
app.config['MYSQL_DB'] = 'crud'

mysql = MySQL(app)

# Test MySQL connection
def test_mysql_connection():
    try:
        with mysql.connection.cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"MySQL connection error: {e}")
        return False

# Home Route - Fetch All Students
@app.route('/')
def Index():
    if not test_mysql_connection():
        return "Failed to connect to MySQL database. Check your configuration."
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        data = cur.fetchall()
        cur.close()
        return render_template('index.html', students=data)
    except Exception as e:
        return f"Database query error: {e}"

# Insert Data
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='sha256')

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)", 
                        (name, email, hashed_password))
            mysql.connection.commit()
            cur.close()
            flash("Data Inserted Successfully", "success")
        except Exception as e:
            flash(f"Database error: {e}", "danger")

        return redirect(url_for('Index'))

# Delete Record (With Error Handling)
@app.route('/delete/<int:id_data>', methods=['GET'])
def delete(id_data):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id=%s", (id_data,))
        record = cur.fetchone()
        if not record:
            flash("Record not found", "warning")
        else:
            cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
            mysql.connection.commit()
            flash("Record Has Been Deleted Successfully", "success")
        cur.close()
    except Exception as e:
        flash(f"Error deleting record: {e}", "danger")
    
    return redirect(url_for('Index'))

# Update Record (With Error Handling)
@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='sha256')

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE students 
            SET name=%s, email=%s, password=%s
            WHERE id=%s
            """, (name, email, hashed_password, id_data))
            mysql.connection.commit()
            cur.close()
            flash("Data Updated Successfully", "success")
        except Exception as e:
            flash(f"Update error: {e}", "danger")

        return redirect(url_for('Index'))

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)  
