import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "hotel_management_db")
    )

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data = request.json
            cursor.execute(
                """INSERT INTO CUSTOMER (FirstName, LastName, CNIC_Passport, Email, Phone, Address)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (data['FirstName'], data['LastName'], data['CNIC_Passport'],
                 data.get('Email'), data['Phone'], data.get('Address'))
            )
            db.commit()
            new_id = cursor.lastrowid
            return jsonify({"message": "Customer created", "CustomerID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM CUSTOMER")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/rooms', methods=['GET'])
def get_rooms():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ROOM")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data = request.json
        cursor.execute(
            "UPDATE ROOM SET Status=%s WHERE RoomID=%s",
            (data['Status'], room_id)
        )
        db.commit()
        return jsonify({"message": "Room updated"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data = request.json
            cursor.execute(
                """INSERT INTO RESERVATION
                   (CustomerID, RoomID, CheckInDate, CheckOutDate, ReservationDate, NumberOfGuests, ReservationStatus)
                   VALUES (%s, %s, %s, %s, CURDATE(), %s, %s)""",
                (data['CustomerID'], data['RoomID'], data['CheckInDate'],
                 data['CheckOutDate'], data['NumberOfGuests'],
                 data.get('ReservationStatus', 'Pending'))
            )
            new_reservation_id = cursor.lastrowid

            # Reflect that the room is now occupied
            cursor.execute(
                "UPDATE ROOM SET Status='Occupied' WHERE RoomID=%s",
                (data['RoomID'],)
            )

            # Create the linked payment record for this reservation
            cursor.execute(
                """INSERT INTO PAYMENT (ReservationID, Amount, PaymentDate, PaymentMethod, PaymentStatus)
                   VALUES (%s, %s, CURDATE(), %s, 'Pending')""",
                (new_reservation_id, data['Amount'], data.get('PaymentMethod', 'Cash'))
            )

            db.commit()
            return jsonify({"message": "Reservation created", "ReservationID": new_reservation_id}), 201
        else:
            cursor.execute("SELECT * FROM RESERVATION ORDER BY ReservationID DESC")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/reservations/<int:res_id>', methods=['PUT', 'DELETE'])
def update_or_cancel_reservation(res_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'PUT':
            data = request.json
            cursor.execute(
                "UPDATE RESERVATION SET ReservationStatus=%s WHERE ReservationID=%s",
                (data['ReservationStatus'], res_id)
            )
            db.commit()
            return jsonify({"message": "Reservation updated"})
        else:
            cursor.execute(
                "UPDATE RESERVATION SET ReservationStatus='Cancelled' WHERE ReservationID=%s",
                (res_id,)
            )
            db.commit()
            return jsonify({"message": "Reservation cancelled"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/payments', methods=['GET'])
def get_payments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PAYMENT")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data = request.json
        cursor.execute(
            "UPDATE PAYMENT SET PaymentStatus=%s WHERE PaymentID=%s",
            (data['PaymentStatus'], payment_id)
        )
        db.commit()
        return jsonify({"message": "Payment updated"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/employees', methods=['GET', 'POST'])
def get_employees():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data = request.json
            cursor.execute(
                """INSERT INTO EMPLOYEE (BranchID, FirstName, LastName, Position, Salary, Phone)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (data['BranchID'], data['FirstName'], data['LastName'],
                 data['Position'], data['Salary'], data.get('Phone'))
            )
            db.commit()
            new_id = cursor.lastrowid
            return jsonify({"message": "Employee created", "EmployeeID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM EMPLOYEE")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/services', methods=['GET', 'POST'])
def get_services():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data = request.json
            cursor.execute(
                "INSERT INTO SERVICE (ServiceName, ServicePrice) VALUES (%s, %s)",
                (data['ServiceName'], data['ServicePrice'])
            )
            db.commit()
            new_id = cursor.lastrowid
            return jsonify({"message": "Service created", "ServiceID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM SERVICE")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/room-types')
def get_room_types():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ROOMTYPE")
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

@app.route('/revenue-by-branch')
def revenue_by_branch():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT B.BranchID, B.BranchName, COALESCE(SUM(P.Amount), 0) AS Revenue
        FROM BRANCH B
        LEFT JOIN ROOM RM        ON RM.BranchID = B.BranchID
        LEFT JOIN RESERVATION R  ON R.RoomID = RM.RoomID
        LEFT JOIN PAYMENT P      ON P.ReservationID = R.ReservationID AND P.PaymentStatus = 'Paid'
        GROUP BY B.BranchID, B.BranchName
        ORDER BY Revenue DESC
    """)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/recent-activity')
def recent_activity():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 'reservation' AS Type, R.ReservationID AS RefID,
               C.FirstName, C.LastName, R.ReservationStatus AS Detail,
               R.ReservationDate AS EventDate
        FROM RESERVATION R
        JOIN CUSTOMER C ON C.CustomerID = R.CustomerID
        ORDER BY R.ReservationID DESC
        LIMIT 5
    """)
    reservations_activity = cursor.fetchall()

    cursor.execute("""
        SELECT 'payment' AS Type, P.PaymentID AS RefID,
               C.FirstName, C.LastName, P.PaymentMethod AS Detail,
               P.PaymentDate AS EventDate, P.Amount
        FROM PAYMENT P
        JOIN RESERVATION R ON R.ReservationID = P.ReservationID
        JOIN CUSTOMER C ON C.CustomerID = R.CustomerID
        ORDER BY P.PaymentID DESC
        LIMIT 5
    """)
    payments_activity = cursor.fetchall()
    db.close()

    combined = reservations_activity + payments_activity
    combined.sort(key=lambda x: str(x['EventDate']), reverse=True)
    for item in combined:
        item['EventDate'] = str(item['EventDate'])

    return jsonify(combined[:6])

if __name__ == '__main__':
    app.run(debug=True)