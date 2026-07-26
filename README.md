# Pearl Hotels — Hotel & Reservation Management System

A full-stack, multi-branch hotel management platform built for Pearl Hotels & Royal Stay Hotels. It replaces manual booking logs with a single dashboard that handles reservations, room availability, billing, staff records, and guest services in real time — backed by a properly normalized relational database rather than flat spreadsheets.

The project was built to demonstrate practical, end-to-end database and backend design: a 3NF-normalized MySQL schema with enforced referential integrity, a Flask REST API that wraps every table in safe transactional endpoints, authenticated access with hashed credentials, and a live dashboard that reflects the true state of the business as soon as any action happens — book a room and it goes Occupied, create a reservation and a Pending payment is generated automatically, mark it Paid and the day's revenue updates instantly.

## Screenshots

**Login**
![Login](./screenshots/login.png)

**Dashboard**
![Dashboard](./screenshots/dashboard.png)

**Reservations**
![Reservations](./screenshots/reservations.png)

**Rooms**
![Rooms](./screenshots/rooms.png)

**Customers**
![Customers](./screenshots/customers.png)

**Payments**
![Payments](./screenshots/payments.png)

**Employees**
![Employees](./screenshots/employees.png)

**Services**
![Services](./screenshots/services.png)

**Branches**
![Branches](./screenshots/branches.png)

## Features

- Real-time dashboard with live occupancy, revenue, and booking statistics
- Reservation management with automatic linked payment record creation, in a single atomic transaction
- Room availability and status tracking across branches, with a visual room map
- Customer records management
- Payment tracking and billing, with status updates reflected instantly on the dashboard
- Employee/staff directory with full CRUD
- Hotel services catalog, with guest service bookings linked to individual reservations
- Soft-delete handling for services already tied to booking history, instead of a hard failure
- Multi-branch support (Lahore and Islamabad)
- Authenticated access — no dashboard data is reachable without logging in
- Fully responsive layout, including a collapsible mobile navigation sidebar

## Tech Stack

- **Database:** MySQL (3NF normalized, 10 tables, constraints, indexes)
- **Backend:** Python, Flask REST API
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Security:** bcrypt password hashing, Flask-Limiter rate limiting, API-key-authenticated endpoints

## Database Design

- 10 normalized tables (Hotel, Branch, RoomType, Room, Customer, Employee, Reservation, Payment, Service, ServiceBooking)
- Primary Keys, Foreign Keys, CHECK constraints, and indexes for query optimization
- 12 SQL queries covering JOINs, aggregations, subqueries, and GROUP BY, used to power dashboard analytics and reporting
- Referential integrity enforced at the database level — for example, a Service tied to existing bookings cannot be deleted outright; the API detects the foreign key constraint and deactivates it instead, preserving historical billing accuracy

## Security

- **Authentication:** Single-admin login gate. The API key required for every data endpoint is never stored in the frontend — it's issued by the server only after a successful login, and kept in `sessionStorage` for the duration of the session.
- **Password storage:** The admin password is never stored or compared in plain text. It's hashed with `bcrypt` and only the hash lives in `.env`.
- **Rate limiting:** The `/login` route is limited to 5 attempts per minute per IP address (via `Flask-Limiter`) to slow brute-force attempts.
- **Same-origin serving:** The frontend is served directly by Flask (`/`) rather than as a separate static file, which avoids CORS misconfiguration entirely and keeps the app self-contained for deployment.
- **Parameterized queries throughout** — no raw string interpolation into SQL anywhere in the codebase.

## How to Run

### 1. Clone the repository
```
git clone https://github.com/Muhammad-Anas59/Hotel-and-Reservation-Management-System.git
cd Hotel-and-Reservation-Management-System
```

### 2. Set up the database
Import `SQL Database.sql` into your local MySQL server.

### 3. Create a `.env` file in the project root
```
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name

API_KEY=generate_a_random_string_here
ALLOWED_ORIGINS=http://localhost:5500

ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=generate_this_in_step_5

FLASK_DEBUG=False
```

Generate a random `API_KEY` with:
```
python -c "import secrets; print(secrets.token_hex(24))"
```

### 4. Create a virtual environment and install dependencies
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5. Generate your admin password hash
Pick a password, then run:
```
python -c "import bcrypt; print(bcrypt.hashpw(b'your_chosen_password', bcrypt.gensalt()).decode())"
```
Paste the output into `.env` as `ADMIN_PASSWORD_HASH`. The plain password itself is never stored anywhere — only the hash.

### 6. Run the application
```
python App.py
```

### 7. Open the app
Go to **http://127.0.0.1:5000** in your browser and log in with the admin username and the password you chose in step 5. The frontend, API, and login are all served from this single address — there's no separate file to open.

