import os
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Only allow requests from these origins (comma-separated in .env for multiple)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS(app, origins=ALLOWED_ORIGINS)

API_KEY = os.getenv("API_KEY")

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not API_KEY or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "hotel_management_db")
    )

def get_json_body():
    """Safely parse the JSON body. Returns (data, None) on success,
    or (None, error_response) if the body is missing/invalid."""
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    return data, None


def require_fields(data, fields):
    """Check that all required fields are present and non-empty.
    Returns an error response if something is missing, else None."""
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400
    return None


@app.route('/customers', methods=['GET', 'POST'])
@require_api_key
def customers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['FirstName', 'LastName', 'CNIC_Passport', 'Phone'])
            if error:
                return error

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
@require_api_key
def get_rooms():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ROOM")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/rooms/<int:room_id>', methods=['PUT'])
@require_api_key
def update_room(room_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data, err = get_json_body()
        if err:
            return err
        error = require_fields(data, ['Status'])
        if error:
            return error

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
@require_api_key
def reservations():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['CustomerID', 'RoomID', 'CheckInDate', 'CheckOutDate', 'NumberOfGuests', 'Amount'])
            if error:
                return error

            # Check for overlapping reservations on the same room
            cursor.execute(
                """SELECT ReservationID FROM RESERVATION
                   WHERE RoomID = %s
                     AND ReservationStatus != 'Cancelled'
                     AND CheckInDate < %s
                     AND CheckOutDate > %s""",
                (data['RoomID'], data['CheckOutDate'], data['CheckInDate'])
            )
            conflict = cursor.fetchone()
            if conflict:
                return jsonify({"error": "Room is already booked for the selected dates"}), 409

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
@require_api_key
def update_or_cancel_reservation(res_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ReservationStatus'])
            if error:
                return error
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
@require_api_key
def get_payments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM PAYMENT")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/payments/<int:payment_id>', methods=['PUT'])
@require_api_key
def update_payment(payment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data, err = get_json_body()
        if err:
            return err
        error = require_fields(data, ['PaymentStatus'])
        if error:
            return error
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
@require_api_key
def get_employees():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchID', 'FirstName', 'LastName', 'Position', 'Salary'])
            if error:
                return error
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

@app.route('/employees/<int:employee_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_employee(employee_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchID', 'FirstName', 'LastName', 'Position', 'Salary'])
            if error:
                return error
            cursor.execute(
                """UPDATE EMPLOYEE SET BranchID=%s, FirstName=%s, LastName=%s, Position=%s, Salary=%s, Phone=%s
                   WHERE EmployeeID=%s""",
                (data['BranchID'], data['FirstName'], data['LastName'],
                 data['Position'], data['Salary'], data.get('Phone'), employee_id)
            )
            db.commit()
            return jsonify({"message": "Employee updated"})
        else:
            cursor.execute("DELETE FROM EMPLOYEE WHERE EmployeeID=%s", (employee_id,))
            db.commit()
            return jsonify({"message": "Employee deleted"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/services', methods=['GET', 'POST'])
@require_api_key
def get_services():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ServiceName', 'ServicePrice'])
            if error:
                return error
            cursor.execute(
                "INSERT INTO SERVICE (ServiceName, ServicePrice, IsActive) VALUES (%s, %s, 1)",
                (data['ServiceName'], data['ServicePrice'])
            )
            db.commit()
            new_id = cursor.lastrowid
            return jsonify({"message": "Service created", "ServiceID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM SERVICE ORDER BY IsActive DESC, ServiceID")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/services/<int:service_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_service(service_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ServiceName', 'ServicePrice'])
            if error:
                return error
            cursor.execute(
                "UPDATE SERVICE SET ServiceName=%s, ServicePrice=%s WHERE ServiceID=%s",
                (data['ServiceName'], data['ServicePrice'], service_id)
            )
            db.commit()
            return jsonify({"message": "Service updated"})
        else:
            try:
                cursor.execute("DELETE FROM SERVICE WHERE ServiceID=%s", (service_id,))
                db.commit()
                return jsonify({"message": "Service deleted"})
            except mysql.connector.Error:
                db.rollback()
                cursor.execute("UPDATE SERVICE SET IsActive=0 WHERE ServiceID=%s", (service_id,))
                db.commit()
                return jsonify({"message": "Service is used in existing bookings, so it was deactivated instead of deleted"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/room-types')
@require_api_key
def get_room_types():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ROOMTYPE")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/hotels')
@require_api_key
def get_hotels():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM HOTEL")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)

@app.route('/branches', methods=['GET', 'POST'])
@require_api_key
def branches():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchName', 'BranchAddress', 'HotelID'])
            if error:
                return error
            cursor.execute(
                "INSERT INTO BRANCH (BranchName, BranchAddress, BranchPhone, HotelID) VALUES (%s, %s, %s, %s)",
                (data['BranchName'], data['BranchAddress'], data.get('BranchPhone'), data['HotelID'])
            )
            db.commit()
            new_id = cursor.lastrowid
            return jsonify({"message": "Branch created", "BranchID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM BRANCH")
            return jsonify(cursor.fetchall())
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/branches/<int:branch_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_branch(branch_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchName', 'BranchAddress', 'HotelID'])
            if error:
                return error
            cursor.execute(
                "UPDATE BRANCH SET BranchName=%s, BranchAddress=%s, BranchPhone=%s, HotelID=%s WHERE BranchID=%s",
                (data['BranchName'], data['BranchAddress'], data.get('BranchPhone'), data['HotelID'], branch_id)
            )
            db.commit()
            return jsonify({"message": "Branch updated"})
        else:
            cursor.execute("DELETE FROM BRANCH WHERE BranchID=%s", (branch_id,))
            db.commit()
            return jsonify({"message": "Branch deleted"})
    except mysql.connector.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route('/revenue-by-branch')
@require_api_key
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
@require_api_key
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
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    if debug_mode:
        app.run(debug=True)
    else:
        from waitress import serve
        port = int(os.getenv("PORT", 5000))
        print(f"Starting production server on port {port}...")
        serve(app, host="0.0.0.0", port=port)