import os
import bcrypt
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Only allow requests from these origins (comma-separated in .env for multiple)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS(app, origins=ALLOWED_ORIGINS)

API_KEY = os.getenv("API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

limiter = Limiter(get_remote_address, app=app, default_limits=[])


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not API_KEY or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def get_db():
    """Connect to Postgres. Render gives a single DATABASE_URL — if present,
    use it directly. Otherwise fall back to discrete DB_* vars for local dev."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME", "hotel_management_db"),
        port=os.getenv("DB_PORT", "5432")
    )


def get_cursor(db):
    """Dict-style cursor — mirrors mysql.connector's cursor(dictionary=True)."""
    return db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def get_json_body():
    data = request.get_json(silent=True)
    if data is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    return data, None


def require_fields(data, fields):
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400
    return None


@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'hotel_management.html')


@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Public route — checks the admin username/password from .env and, if
    correct, hands back the API key the frontend needs for every other
    request. Password is compared against a bcrypt hash, never in plain
    text, and this route is rate-limited to 5 attempts per minute per IP."""
    data, err = get_json_body()
    if err:
        return err
    error = require_fields(data, ['username', 'password'])
    if error:
        return error

    if not ADMIN_PASSWORD_HASH:
        return jsonify({"error": "Server misconfigured: ADMIN_PASSWORD_HASH is not set"}), 500

    password_matches = bcrypt.checkpw(
        data['password'].encode('utf-8'),
        ADMIN_PASSWORD_HASH.encode('utf-8')
    )

    if data['username'] == ADMIN_USERNAME and password_matches:
        if not API_KEY:
            return jsonify({"error": "Server misconfigured: API_KEY is not set"}), 500
        return jsonify({"apiKey": API_KEY}), 200

    return jsonify({"error": "Invalid username or password"}), 401


@app.route('/customers', methods=['GET', 'POST'])
@require_api_key
def customers():
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['FirstName', 'LastName', 'CNIC_Passport', 'Phone'])
            if error:
                return error

            cursor.execute(
                """INSERT INTO customer ("FirstName", "LastName", "CNIC_Passport", "Email", "Phone", "Address")
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING "CustomerID" """,
                (data['FirstName'], data['LastName'], data['CNIC_Passport'],
                 data.get('Email'), data['Phone'], data.get('Address'))
            )
            new_id = cursor.fetchone()['CustomerID']
            db.commit()
            return jsonify({"message": "Customer created", "CustomerID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM customer")
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/rooms', methods=['GET'])
@require_api_key
def get_rooms():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM room")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


@app.route('/rooms/<int:room_id>', methods=['PUT'])
@require_api_key
def update_room(room_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        data, err = get_json_body()
        if err:
            return err
        error = require_fields(data, ['Status'])
        if error:
            return error

        cursor.execute(
            'UPDATE room SET "Status"=%s WHERE "RoomID"=%s',
            (data['Status'], room_id)
        )
        db.commit()
        return jsonify({"message": "Room updated"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/reservations', methods=['GET', 'POST'])
@require_api_key
def reservations():
    db = get_db()
    cursor = get_cursor(db)
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
                """SELECT "ReservationID" FROM reservation
                   WHERE "RoomID" = %s
                     AND "ReservationStatus" != 'Cancelled'
                     AND "CheckInDate" < %s
                     AND "CheckOutDate" > %s""",
                (data['RoomID'], data['CheckOutDate'], data['CheckInDate'])
            )
            conflict = cursor.fetchone()
            if conflict:
                return jsonify({"error": "Room is already booked for the selected dates"}), 409

            cursor.execute(
                """INSERT INTO reservation
                   ("CustomerID", "RoomID", "CheckInDate", "CheckOutDate", "ReservationDate", "NumberOfGuests", "ReservationStatus")
                   VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s) RETURNING "ReservationID" """,
                (data['CustomerID'], data['RoomID'], data['CheckInDate'],
                 data['CheckOutDate'], data['NumberOfGuests'],
                 data.get('ReservationStatus', 'Pending'))
            )
            new_reservation_id = cursor.fetchone()['ReservationID']

            # Reflect that the room is now occupied
            cursor.execute(
                'UPDATE room SET "Status"=\'Occupied\' WHERE "RoomID"=%s',
                (data['RoomID'],)
            )

            # Create the linked payment record for this reservation
            cursor.execute(
                """INSERT INTO payment ("ReservationID", "Amount", "PaymentDate", "PaymentMethod", "PaymentStatus")
                   VALUES (%s, %s, CURRENT_DATE, %s, 'Pending')""",
                (new_reservation_id, data['Amount'], data.get('PaymentMethod', 'Cash'))
            )

            db.commit()
            return jsonify({"message": "Reservation created", "ReservationID": new_reservation_id}), 201
        else:
            cursor.execute('SELECT * FROM reservation ORDER BY "ReservationID" DESC')
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/reservations/<int:res_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_cancel_reservation(res_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ReservationStatus'])
            if error:
                return error
            cursor.execute(
                'UPDATE reservation SET "ReservationStatus"=%s WHERE "ReservationID"=%s',
                (data['ReservationStatus'], res_id)
            )
            db.commit()
            return jsonify({"message": "Reservation updated"})
        else:
            cursor.execute(
                'UPDATE reservation SET "ReservationStatus"=\'Cancelled\' WHERE "ReservationID"=%s',
                (res_id,)
            )
            db.commit()
            return jsonify({"message": "Reservation cancelled"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/payments', methods=['GET'])
@require_api_key
def get_payments():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM payment")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


@app.route('/payments/<int:payment_id>', methods=['PUT'])
@require_api_key
def update_payment(payment_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        data, err = get_json_body()
        if err:
            return err
        error = require_fields(data, ['PaymentStatus'])
        if error:
            return error
        cursor.execute(
            'UPDATE payment SET "PaymentStatus"=%s WHERE "PaymentID"=%s',
            (data['PaymentStatus'], payment_id)
        )
        db.commit()
        return jsonify({"message": "Payment updated"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/employees', methods=['GET', 'POST'])
@require_api_key
def get_employees():
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchID', 'FirstName', 'LastName', 'Position', 'Salary'])
            if error:
                return error
            cursor.execute(
                """INSERT INTO employee ("BranchID", "FirstName", "LastName", "Position", "Salary", "Phone")
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING "EmployeeID" """,
                (data['BranchID'], data['FirstName'], data['LastName'],
                 data['Position'], data['Salary'], data.get('Phone'))
            )
            new_id = cursor.fetchone()['EmployeeID']
            db.commit()
            return jsonify({"message": "Employee created", "EmployeeID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM employee")
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/employees/<int:employee_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_employee(employee_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchID', 'FirstName', 'LastName', 'Position', 'Salary'])
            if error:
                return error
            cursor.execute(
                """UPDATE employee SET "BranchID"=%s, "FirstName"=%s, "LastName"=%s, "Position"=%s, "Salary"=%s, "Phone"=%s
                   WHERE "EmployeeID"=%s""",
                (data['BranchID'], data['FirstName'], data['LastName'],
                 data['Position'], data['Salary'], data.get('Phone'), employee_id)
            )
            db.commit()
            return jsonify({"message": "Employee updated"})
        else:
            cursor.execute('DELETE FROM employee WHERE "EmployeeID"=%s', (employee_id,))
            db.commit()
            return jsonify({"message": "Employee deleted"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/services', methods=['GET', 'POST'])
@require_api_key
def get_services():
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ServiceName', 'ServicePrice'])
            if error:
                return error
            cursor.execute(
                'INSERT INTO service ("ServiceName", "ServicePrice", "IsActive") VALUES (%s, %s, 1) RETURNING "ServiceID"',
                (data['ServiceName'], data['ServicePrice'])
            )
            new_id = cursor.fetchone()['ServiceID']
            db.commit()
            return jsonify({"message": "Service created", "ServiceID": new_id}), 201
        else:
            cursor.execute('SELECT * FROM service ORDER BY "IsActive" DESC, "ServiceID"')
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/services/<int:service_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_service(service_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ServiceName', 'ServicePrice'])
            if error:
                return error
            cursor.execute(
                'UPDATE service SET "ServiceName"=%s, "ServicePrice"=%s WHERE "ServiceID"=%s',
                (data['ServiceName'], data['ServicePrice'], service_id)
            )
            db.commit()
            return jsonify({"message": "Service updated"})
        else:
            try:
                cursor.execute('DELETE FROM service WHERE "ServiceID"=%s', (service_id,))
                db.commit()
                return jsonify({"message": "Service deleted"})
            except psycopg2.Error:
                db.rollback()
                cursor.execute('UPDATE service SET "IsActive"=0 WHERE "ServiceID"=%s', (service_id,))
                db.commit()
                return jsonify({"message": "Service is used in existing bookings, so it was deactivated instead of deleted"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/service-bookings', methods=['GET', 'POST'])
@require_api_key
def service_bookings():
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['ReservationID', 'ServiceID', 'ServiceDate'])
            if error:
                return error

            cursor.execute('SELECT "IsActive" FROM service WHERE "ServiceID"=%s', (data['ServiceID'],))
            svc = cursor.fetchone()
            if not svc:
                return jsonify({"error": "Service not found"}), 404
            if not svc['IsActive']:
                return jsonify({"error": "This service is no longer available to book"}), 400

            cursor.execute(
                """INSERT INTO service_booking ("ReservationID", "ServiceID", "Quantity", "ServiceDate")
                   VALUES (%s, %s, %s, %s) RETURNING "ServiceBookingID" """,
                (data['ReservationID'], data['ServiceID'], data.get('Quantity', 1), data['ServiceDate'])
            )
            new_id = cursor.fetchone()['ServiceBookingID']
            db.commit()
            return jsonify({"message": "Service booking created", "ServiceBookingID": new_id}), 201
        else:
            cursor.execute("""
                SELECT sb."ServiceBookingID", sb."ReservationID", sb."ServiceID", sb."Quantity", sb."ServiceDate",
                       s."ServiceName", s."ServicePrice",
                       c."FirstName", c."LastName"
                FROM service_booking sb
                JOIN service s ON s."ServiceID" = sb."ServiceID"
                JOIN reservation r ON r."ReservationID" = sb."ReservationID"
                JOIN customer c ON c."CustomerID" = r."CustomerID"
                ORDER BY sb."ServiceBookingID" DESC
            """)
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/service-bookings/<int:booking_id>', methods=['DELETE'])
@require_api_key
def delete_service_booking(booking_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        cursor.execute('DELETE FROM service_booking WHERE "ServiceBookingID"=%s', (booking_id,))
        db.commit()
        return jsonify({"message": "Service booking deleted"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/room-types')
@require_api_key
def get_room_types():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM roomtype")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


@app.route('/hotels')
@require_api_key
def get_hotels():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("SELECT * FROM hotel")
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


@app.route('/branches', methods=['GET', 'POST'])
@require_api_key
def branches():
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'POST':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchName', 'BranchAddress', 'HotelID'])
            if error:
                return error
            cursor.execute(
                'INSERT INTO branch ("BranchName", "BranchAddress", "BranchPhone", "HotelID") VALUES (%s, %s, %s, %s) RETURNING "BranchID"',
                (data['BranchName'], data['BranchAddress'], data.get('BranchPhone'), data['HotelID'])
            )
            new_id = cursor.fetchone()['BranchID']
            db.commit()
            return jsonify({"message": "Branch created", "BranchID": new_id}), 201
        else:
            cursor.execute("SELECT * FROM branch")
            return jsonify(cursor.fetchall())
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/branches/<int:branch_id>', methods=['PUT', 'DELETE'])
@require_api_key
def update_or_delete_branch(branch_id):
    db = get_db()
    cursor = get_cursor(db)
    try:
        if request.method == 'PUT':
            data, err = get_json_body()
            if err:
                return err
            error = require_fields(data, ['BranchName', 'BranchAddress', 'HotelID'])
            if error:
                return error
            cursor.execute(
                'UPDATE branch SET "BranchName"=%s, "BranchAddress"=%s, "BranchPhone"=%s, "HotelID"=%s WHERE "BranchID"=%s',
                (data['BranchName'], data['BranchAddress'], data.get('BranchPhone'), data['HotelID'], branch_id)
            )
            db.commit()
            return jsonify({"message": "Branch updated"})
        else:
            cursor.execute('DELETE FROM branch WHERE "BranchID"=%s', (branch_id,))
            db.commit()
            return jsonify({"message": "Branch deleted"})
    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()


@app.route('/revenue-by-branch')
@require_api_key
def revenue_by_branch():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("""
        SELECT B."BranchID", B."BranchName", COALESCE(SUM(P."Amount"), 0) AS "Revenue"
        FROM branch B
        LEFT JOIN room RM        ON RM."BranchID" = B."BranchID"
        LEFT JOIN reservation R  ON R."RoomID" = RM."RoomID"
        LEFT JOIN payment P      ON P."ReservationID" = R."ReservationID" AND P."PaymentStatus" = 'Paid'
        GROUP BY B."BranchID", B."BranchName"
        ORDER BY "Revenue" DESC
    """)
    data = cursor.fetchall()
    db.close()
    return jsonify(data)


@app.route('/recent-activity')
@require_api_key
def recent_activity():
    db = get_db()
    cursor = get_cursor(db)
    cursor.execute("""
        SELECT 'reservation' AS "Type", R."ReservationID" AS "RefID",
               C."FirstName", C."LastName", R."ReservationStatus" AS "Detail",
               R."ReservationDate" AS "EventDate"
        FROM reservation R
        JOIN customer C ON C."CustomerID" = R."CustomerID"
        ORDER BY R."ReservationID" DESC
        LIMIT 5
    """)
    reservations_activity = cursor.fetchall()

    cursor.execute("""
        SELECT 'payment' AS "Type", P."PaymentID" AS "RefID",
               C."FirstName", C."LastName", P."PaymentMethod" AS "Detail",
               P."PaymentDate" AS "EventDate", P."Amount"
        FROM payment P
        JOIN reservation R ON R."ReservationID" = P."ReservationID"
        JOIN customer C ON C."CustomerID" = R."CustomerID"
        ORDER BY P."PaymentID" DESC
        LIMIT 5
    """)
    payments_activity = cursor.fetchall()
    db.close()

    combined = list(reservations_activity) + list(payments_activity)
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