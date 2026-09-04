# Pearl Hotels — Hotel & Reservation Management System

🔗 **Live App:** [pearl-hotels-management-system.duckdns.org](https://pearl-hotels-management-system.duckdns.org)
📂 **Repo:** [github.com/Muhammad-Anas59/Hotel-and-Reservation-Management-System](https://github.com/Muhammad-Anas59/Hotel-and-Reservation-Management-System)

A full-stack, multi-branch hotel management platform built for Pearl Hotels & Royal Stay Hotels. It replaces manual booking logs with a single dashboard that handles reservations, room availability, billing, staff records, and guest services in real time — backed by a properly normalized relational database rather than flat spreadsheets.

The project was built to demonstrate practical, end-to-end database and backend design: a 3NF-normalized relational schema with enforced referential integrity, a Flask REST API that wraps every table in safe transactional endpoints, authenticated access with hashed credentials, and a live dashboard that reflects the true state of the business as soon as any action happens — book a room and it goes Occupied, create a reservation and a Pending payment is generated automatically, mark it Paid and the day's revenue updates instantly.

It's deployed and running in production on AWS EC2, containerized with Docker and backed by PostgreSQL.

## Screenshots

**Login**
![Login](./screenshots/Login.png)

**Dashboard**
![Dashboard](./screenshots/Dashboard.png)

**Reservations**
![Reservations](./screenshots/Reservations.png)

**Rooms**
![Rooms](./screenshots/Rooms.png)

**Customers**
![Customers](./screenshots/Customers.png)

**Payments**
![Payments](./screenshots/Payments.png)

**Employees**
![Employees](./screenshots/Employees.png)

**Services**
![Services](./screenshots/Services.png)

**Branches**
![Branches](./screenshots/Branches.png)

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

- **Database:** PostgreSQL (3NF normalized, 10 tables, constraints, indexes)
- **Backend:** Python, Flask REST API, served via Waitress
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Infrastructure:** Docker & Docker Compose, AWS EC2, Nginx reverse proxy, Let's Encrypt SSL (Certbot), DuckDNS
- **Security:** bcrypt password hashing, Flask-Limiter rate limiting, API-key-authenticated endpoints

## Database Design

- 10 normalized tables (Hotel, Branch, RoomType, Room, Customer, Employee, Reservation, Payment, Service, ServiceBooking)
- Primary Keys, Foreign Keys, CHECK constraints, and indexes for query optimization
- 12+ SQL queries covering JOINs, aggregations, subqueries, and GROUP BY, used to power dashboard analytics and reporting
- Referential integrity enforced at the database level — for example, a Service tied to existing bookings cannot be deleted outright; the API detects the foreign key constraint and deactivates it instead, preserving historical billing accuracy

## Deployment

The app runs in production on a self-managed **AWS EC2 instance** (Ubuntu, t3.micro, within the AWS Free Tier), containerized with **Docker Compose**:

- The Flask app and PostgreSQL each run in their own isolated container, on a private Docker network — Postgres is not exposed outside the host.
- **Nginx** runs on the host as a reverse proxy, routing public traffic on ports 80/443 to the app container's internal port.
- **Certbot** (Let's Encrypt) issues and auto-renews a free SSL certificate for the public domain.
- The public domain (`pearl-hotels-management-system.duckdns.org`) is a free dynamic DNS hostname from **DuckDNS**, pointed at the EC2 instance's public IP.
- Secrets (DB credentials, API key, admin password hash) are kept in environment files (`.env` / `app.env`) on the server, excluded from git via `.gitignore`, and never committed to the repo.
- Data persists in a named Docker volume, independent of container restarts/rebuilds.

Originally built against MySQL, the project was fully migrated to PostgreSQL for deployment. A few real differences had to be handled during the migration, rather than a drop-in swap:

- **Identifier casing** — PostgreSQL folds unquoted identifiers to lowercase by default, while the original schema and frontend relied on exact mixed-case keys (e.g. `HotelID`). Every column reference is explicitly double-quoted in the schema to preserve exact casing; table names were kept lowercase to match how the API queries them.
- **Auto-increment behavior** — `AUTO_INCREMENT` → `SERIAL`, and `cursor.lastrowid` (MySQL-specific) was replaced with `RETURNING` on every `INSERT`.
- **Date functions** — `CURDATE()` → `CURRENT_DATE`.
- **Sequence continuity** — after loading sample data with explicit IDs, each table's sequence counter is reset with `setval(pg_get_serial_sequence(...))` so the next real record created by the app doesn't collide with existing sample IDs.

## Security

- **Authentication:** Single-admin login gate. The API key required for every data endpoint is never stored in the frontend — it's issued by the server only after a successful login, and kept in `sessionStorage` for the duration of the session.
- **Password storage:** The admin password is never stored or compared in plain text. It's hashed with `bcrypt` and only the hash lives in the environment config.
- **Rate limiting:** The `/login` route is limited to 5 attempts per minute per IP address (via `Flask-Limiter`) to slow brute-force attempts.
- **Same-origin serving:** The frontend is served directly by Flask (`/`) rather than as a separate static file, which avoids CORS misconfiguration entirely and keeps the app self-contained for deployment.
- **Parameterized queries throughout** — no raw string interpolation into SQL anywhere in the codebase.
- **Network isolation:** PostgreSQL is only reachable from the app container (not exposed on the public internet); the raw application port is closed at the firewall level, with all public traffic routed through Nginx over HTTPS.

## Running with Docker (as deployed in production)

```
docker compose up -d --build
```

This builds the Flask app image and starts it alongside a PostgreSQL container, with the schema auto-loaded from `PostGre.sql` on first run. Requires a `.env` (for Compose's own Postgres container config) and an `app.env` (for the Flask app's runtime environment variables) in the project root — see `docker-compose.yml` for the exact variables each expects.

---

Visit the [live application](https://pearl-hotels-management-system.duckdns.org).
