# Hotel and Reservation Management System

A full-stack, multi-branch hotel management platform built for **Pearl Hotels & Royal Stay Hotels**. It replaces manual booking logs with a single dashboard that handles reservations, room availability, billing, and staff records in real time — backed by a properly normalized relational database rather than flat spreadsheets.

The project was built to demonstrate practical, end-to-end database and backend design: a 3NF-normalized MySQL schema with enforced referential integrity, a Flask REST API that wraps every table in safe transactional endpoints, and a live dashboard that reflects the true state of the business as soon as any action happens — book a room and it goes Occupied, create a reservation and a Pending payment is generated automatically, mark it Paid and the day's revenue updates instantly.

## Screenshots

### Dashboard
![Dashboard](Project%20Images/Dashoboard_Preview.png)

### Reservations
![Reservations](Project%20Images/Reservation_Preview.png)

### Rooms
![Rooms](Project%20Images/Rooms_Preview.png)

### Payments
![Payments](Project%20Images/Payments_preview.png)

### Customers
![Customers](Project%20Images/Customers_Preview.png)

### Employees
![Employees](Project%20Images/Employees_Preview.png)

### Services
![Services](Project%20Images/Services_Preview.png)

## Features
- Real-time dashboard with live occupancy, revenue, and booking statistics
- Reservation management with automatic linked payment record creation, in a single atomic transaction
- Room availability and status tracking across branches
- Customer records management
- Payment tracking and billing, with status updates reflected instantly on the dashboard
- Employee/staff directory
- Hotel services management
- Multi-branch support (Lahore and Islamabad)

## Tech Stack
- **Database:** MySQL (3NF normalized, 10 tables, constraints, indexes)
- **Backend:** Python Flask REST API
- **Frontend:** HTML, CSS, Vanilla JavaScript

## Database Design
- 10 normalized tables (Hotel, Branch, RoomType, Room, Customer, Employee, Reservation, Payment, Service, ServiceBooking)
- Primary Keys, Foreign Keys, CHECK constraints, and indexes for query optimization
- 12 SQL queries covering JOINs, aggregations, subqueries, and GROUP BY, used to power dashboard analytics and reporting

## How to Run

1. Clone the repository

   git clone https://github.com/Muhammad-Anas59/Hotel-and-Reservation-Management-System.git
   cd Hotel-and-Reservation-Management-System

2. Set up the database

   Import `SQL Database.sql` into your local MySQL server.

3. Create a `.env` file in the project root with your own database credentials:

   DB_HOST=localhost
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=your_database_name

4. Create a virtual environment and install dependencies

   python -m venv venv
   venv\Scripts\Activate.ps1
   pip install -r requirements.txt

5. Run the Flask backend

   python App.py

6. Open `hotel_management.html` in your browser.