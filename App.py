from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Password12..",
        database="hotel_management_db"
    )

@app.route('/customers')
def get_customers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM CUSTOMER")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/rooms')
def get_rooms():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ROOM")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/reservations')
def get_reservations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM RESERVATION")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/payments')
def get_payments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PAYMENT")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/employees')
def get_employees():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM EMPLOYEE")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/services')
def get_services():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SERVICE")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/branches')
def get_branches():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM BRANCH")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)