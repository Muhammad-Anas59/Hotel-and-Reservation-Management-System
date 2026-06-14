# Hotel and Reservation Management System

A full-stack hotel and reservation management system built for Pearl Hotels & Royal Stay Hotels, featuring a normalized MySQL database, Flask REST API backend, and a professional HTML/CSS dashboard.

## Features
- Real-time dashboard with live statistics
- Reservation management
- Room availability tracking across branches
- Customer records management
- Payment tracking and billing
- Employee/staff directory
- Hotel services management
- Multi-branch support (Lahore and Islamabad)

## Tech Stack
- Database: MySQL (3NF normalized, 10 tables, constraints, indexes)
- Backend: Python Flask REST API
- Frontend: HTML, CSS, Vanilla JavaScript

## Database Design
- 10 normalized tables (Hotel, Branch, RoomType, Room, Customer, Employee, Reservation, Payment, Service, Service Booking)
- Primary Keys, Foreign Keys, CHECK constraints, indexes for optimization
- 12 SQL queries covering JOINs, aggregations, subqueries, and GROUP BY

## How to Run
1. Set up MySQL database using hotel_management_db.sql
2. Run Flask backend: python App.py
3. Open hotel_management.html in browser
