-- =============================================
-- HOTEL MANAGEMENT SYSTEM
-- Database : hotel_management_db
-- =============================================

CREATE DATABASE IF NOT EXISTS hotel_management_db;-- Query 12: Reservations with Payment Status (JOIN)
SELECT R.ReservationID, P.PaymentStatus
FROM RESERVATION R
JOIN PAYMENT P ON R.ReservationID = P.ReservationID;
USE hotel_management_db;

-- =============================================
-- DDL: TABLE CREATION
-- =============================================

CREATE TABLE HOTEL (
  HotelID INT PRIMARY KEY AUTO_INCREMENT,
  HotelName VARCHAR(100) NOT NULL,
  HotelAddress VARCHAR(255) NOT NULL,
  HotelPhone VARCHAR(20) UNIQUE
);

CREATE TABLE BRANCH (
  BranchID INT PRIMARY KEY AUTO_INCREMENT,
  HotelID INT NOT NULL,
  BranchName VARCHAR(100) NOT NULL,
  BranchAddress VARCHAR(255) NOT NULL,
  BranchPhone VARCHAR(20) UNIQUE
);

CREATE TABLE ROOMTYPE (
  RoomTypeID INT PRIMARY KEY AUTO_INCREMENT,
  TypeName VARCHAR(50) NOT NULL,
  Capacity INT NOT NULL CHECK (Capacity > 0),
  PricePerNight DECIMAL(10,2) NOT NULL CHECK (PricePerNight > 0)
);

CREATE TABLE ROOM (
  RoomID INT PRIMARY KEY AUTO_INCREMENT,
  BranchID INT NOT NULL,
  RoomTypeID INT NOT NULL,
  RoomNumber VARCHAR(10) NOT NULL,
  FloorNumber INT NOT NULL,
  Status VARCHAR(20) DEFAULT 'Available' CHECK (Status IN ('Available','Occupied','Maintenance'))
);

CREATE TABLE CUSTOMER (
  CustomerID INT PRIMARY KEY AUTO_INCREMENT,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  CNIC_Passport VARCHAR(20) UNIQUE NOT NULL,
  Email VARCHAR(100) UNIQUE,
  Phone VARCHAR(20) NOT NULL,
  Address VARCHAR(255)
);

CREATE TABLE EMPLOYEE (
  EmployeeID INT PRIMARY KEY AUTO_INCREMENT,
  BranchID INT NOT NULL,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  Position VARCHAR(50) NOT NULL,
  Salary DECIMAL(10,2) CHECK (Salary > 0),
  Phone VARCHAR(20)
);

CREATE TABLE RESERVATION (
  ReservationID INT PRIMARY KEY AUTO_INCREMENT,
  CustomerID INT NOT NULL,
  RoomID INT NOT NULL,
  CheckInDate DATE NOT NULL,
  CheckOutDate DATE NOT NULL,
  ReservationDate DATE NOT NULL,
  NumberOfGuests INT CHECK (NumberOfGuests > 0),
  ReservationStatus VARCHAR(20) DEFAULT 'Pending'
    CHECK (ReservationStatus IN ('Pending','Confirmed','Cancelled','Completed'))
);

CREATE TABLE PAYMENT (
  PaymentID INT PRIMARY KEY AUTO_INCREMENT,
  ReservationID INT NOT NULL,
  Amount DECIMAL(10,2) CHECK (Amount > 0),
  PaymentDate DATE NOT NULL,
  PaymentMethod VARCHAR(30),
  PaymentStatus VARCHAR(20) DEFAULT 'Pending'
    CHECK (PaymentStatus IN ('Pending','Paid','Refunded'))
);

CREATE TABLE SERVICE (
  ServiceID INT PRIMARY KEY AUTO_INCREMENT,
  ServiceName VARCHAR(100) NOT NULL,
  ServicePrice DECIMAL(10,2) CHECK (ServicePrice > 0)
);

CREATE TABLE SERVICE_BOOKING (
  ServiceBookingID INT PRIMARY KEY AUTO_INCREMENT,
  ReservationID INT NOT NULL,
  ServiceID INT NOT NULL,
  Quantity INT CHECK (Quantity > 0),
  ServiceDate DATE NOT NULL
);

-- =============================================
-- FOREIGN KEY RELATIONSHIPS
-- =============================================

ALTER TABLE BRANCH ADD FOREIGN KEY (HotelID) REFERENCES HOTEL(HotelID);
ALTER TABLE ROOM ADD FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID);
ALTER TABLE ROOM ADD FOREIGN KEY (RoomTypeID) REFERENCES ROOMTYPE(RoomTypeID);
ALTER TABLE EMPLOYEE ADD FOREIGN KEY (BranchID) REFERENCES BRANCH(BranchID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (CustomerID) REFERENCES CUSTOMER(CustomerID);
ALTER TABLE RESERVATION ADD FOREIGN KEY (RoomID) REFERENCES ROOM(RoomID);
ALTER TABLE PAYMENT ADD FOREIGN KEY (ReservationID) REFERENCES RESERVATION(ReservationID);
ALTER TABLE SERVICE_BOOKING ADD FOREIGN KEY (ReservationID) REFERENCES RESERVATION(ReservationID);
ALTER TABLE SERVICE_BOOKING ADD FOREIGN KEY (ServiceID) REFERENCES SERVICE(ServiceID);

-- =============================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================

CREATE INDEX idx_reservation_customer ON RESERVATION(CustomerID);
CREATE INDEX idx_reservation_room ON RESERVATION(RoomID);
CREATE INDEX idx_room_branch ON ROOM(BranchID);
CREATE INDEX idx_payment_reservation ON PAYMENT(ReservationID);

-- =============================================
-- DML: DATA INSERTION
-- =============================================

INSERT INTO HOTEL VALUES (1,'Pearl Hotels','Lahore, Pakistan','0421111111');
INSERT INTO HOTEL VALUES (2,'Royal Stay Hotels','Islamabad, Pakistan','0512222222');

INSERT INTO BRANCH VALUES (101,1,'Pearl Gulberg','Gulberg Lahore','0421234567');
INSERT INTO BRANCH VALUES (102,1,'Pearl DHA','DHA Lahore','0422345678');
INSERT INTO BRANCH VALUES (201,2,'Royal Blue Area','Blue Area Islamabad','0513456789');
INSERT INTO BRANCH VALUES (202,2,'Royal F-10','F-10 Islamabad','0514567890');

INSERT INTO ROOMTYPE VALUES (1,'Single',1,5000);
INSERT INTO ROOMTYPE VALUES (2,'Double',2,8000);
INSERT INTO ROOMTYPE VALUES (3,'Deluxe',3,12000);
INSERT INTO ROOMTYPE VALUES (4,'Suite',4,20000);

INSERT INTO ROOM VALUES (1,101,1,'101',1,'Available');
INSERT INTO ROOM VALUES (2,101,2,'102',1,'Occupied');
INSERT INTO ROOM VALUES (3,101,3,'201',2,'Available');
INSERT INTO ROOM VALUES (4,102,1,'103',1,'Maintenance');
INSERT INTO ROOM VALUES (5,102,2,'104',1,'Available');
INSERT INTO ROOM VALUES (6,102,4,'301',3,'Occupied');
INSERT INTO ROOM VALUES (7,201,1,'105',1,'Available');
INSERT INTO ROOM VALUES (8,201,3,'202',2,'Occupied');
INSERT INTO ROOM VALUES (9,201,4,'302',3,'Available');
INSERT INTO ROOM VALUES (10,202,2,'106',1,'Available');
INSERT INTO ROOM VALUES (11,202,3,'203',2,'Occupied');
INSERT INTO ROOM VALUES (12,202,4,'303',3,'Available');

INSERT INTO CUSTOMER VALUES (1,'Ali','Khan','35201-1111111-1','ali@gmail.com','03001111111','Lahore');
INSERT INTO CUSTOMER VALUES (2,'Ahmed','Raza','35201-2222222-2','ahmed@gmail.com','03002222222','Islamabad');
INSERT INTO CUSTOMER VALUES (3,'Usman','Malik','35201-3333333-3','usman@gmail.com','03003333333','Karachi');
INSERT INTO CUSTOMER VALUES (4,'Hassan','Shah','35201-4444444-4','hassan@gmail.com','03004444444','Faisalabad');
INSERT INTO CUSTOMER VALUES (5,'Bilal','Akram','35201-5555555-5','bilal@gmail.com','03005555555','Multan');
INSERT INTO CUSTOMER VALUES (6,'Hamza','Nawaz','35201-6666666-6','hamza@gmail.com','03006666666','Sialkot');
INSERT INTO CUSTOMER VALUES (7,'Saad','Ashraf','35201-7777777-7','saad@gmail.com','03007777777','Lahore');
INSERT INTO CUSTOMER VALUES (8,'Anas','Javed','35201-8888888-8','anas@gmail.com','03008888888','Gujranwala');

INSERT INTO EMPLOYEE VALUES (1,101,'Ayesha','Malik','Manager',90000,'03111111111');
INSERT INTO EMPLOYEE VALUES (2,101,'Sara','Khan','Receptionist',50000,'03112222222');
INSERT INTO EMPLOYEE VALUES (3,102,'Zain','Ali','Manager',90000,'03113333333');
INSERT INTO EMPLOYEE VALUES (4,201,'Umair','Raza','Receptionist',50000,'03114444444');
INSERT INTO EMPLOYEE VALUES (5,202,'Fatima','Noor','Manager',95000,'03115555555');
INSERT INTO EMPLOYEE VALUES (6,202,'Hina','Aslam','Accountant',60000,'03116666666');

INSERT INTO RESERVATION VALUES (1,1,2,'2026-06-10','2026-06-12','2026-06-01',2,'Confirmed');
INSERT INTO RESERVATION VALUES (2,2,6,'2026-06-11','2026-06-14','2026-06-02',2,'Confirmed');
INSERT INTO RESERVATION VALUES (3,3,8,'2026-06-15','2026-06-18','2026-06-03',3,'Pending');
INSERT INTO RESERVATION VALUES (4,4,11,'2026-06-16','2026-06-20','2026-06-04',2,'Confirmed');
INSERT INTO RESERVATION VALUES (5,5,3,'2026-06-21','2026-06-24','2026-06-05',2,'Completed');
INSERT INTO RESERVATION VALUES (6,6,9,'2026-06-22','2026-06-25','2026-06-06',4,'Confirmed');

INSERT INTO PAYMENT VALUES (1,1,16000,'2026-06-01','Card','Paid');
INSERT INTO PAYMENT VALUES (2,2,24000,'2026-06-02','Cash','Paid');
INSERT INTO PAYMENT VALUES (3,3,36000,'2026-06-03','Card','Pending');
INSERT INTO PAYMENT VALUES (4,4,32000,'2026-06-04','Online','Paid');
INSERT INTO PAYMENT VALUES (5,5,36000,'2026-06-05','Cash','Paid');
INSERT INTO PAYMENT VALUES (6,6,60000,'2026-06-06','Card','Paid');

INSERT INTO SERVICE VALUES (1,'Laundry',1000);
INSERT INTO SERVICE VALUES (2,'Spa',3000);
INSERT INTO SERVICE VALUES (3,'Room Service',1500);
INSERT INTO SERVICE VALUES (4,'Airport Pickup',5000);

INSERT INTO SERVICE_BOOKING VALUES (1,1,1,2,'2026-06-10');
INSERT INTO SERVICE_BOOKING VALUES (2,1,3,1,'2026-06-10');
INSERT INTO SERVICE_BOOKING VALUES (3,2,2,1,'2026-06-11');
INSERT INTO SERVICE_BOOKING VALUES (4,4,4,1,'2026-06-16');

-- =============================================
-- SELECT QUERIES
-- =============================================

-- Query 1: Display All Customers
SELECT * FROM CUSTOMER;

-- Query 2: Display Available Rooms
SELECT * FROM ROOM WHERE Status = 'Available';

-- Query 3: Display Confirmed Reservations
SELECT * FROM RESERVATION WHERE ReservationStatus = 'Confirmed';

-- Query 4: Customer Reservation Details (JOIN)
SELECT C.FirstName, C.LastName, R.ReservationID, R.CheckInDate, R.CheckOutDate
FROM CUSTOMER C
JOIN RESERVATION R ON C.CustomerID = R.CustomerID;

-- Query 5: Room Information with Room Type (JOIN)
SELECT RM.RoomNumber, RT.TypeName, RT.PricePerNight
FROM ROOM RM
JOIN ROOMTYPE RT ON RM.RoomTypeID = RT.RoomTypeID;

-- Query 6: Total Revenue Generated (AGGREGATION)
SELECT SUM(Amount) AS TotalRevenue
FROM PAYMENT
WHERE PaymentStatus = 'Paid';

-- Query 7: Count Rooms in Each Branch (GROUP BY)
SELECT BranchID, COUNT(*) AS TotalRooms
FROM ROOM
GROUP BY BranchID;

-- Query 8: Average Salary of Employees (AGGREGATION)
SELECT AVG(Salary) AS AverageSalary
FROM EMPLOYEE;

-- Query 9: Customers Who Made Reservations (SUBQUERY)
SELECT FirstName, LastName
FROM CUSTOMER
WHERE CustomerID IN (SELECT CustomerID FROM RESERVATION);

-- Query 10: Service Usage Report (JOIN)
SELECT S.ServiceName, SB.Quantity
FROM SERVICE S
JOIN SERVICE_BOOKING SB ON S.ServiceID = SB.ServiceID;

-- Query 11: Highest Payment (AGGREGATION)
SELECT MAX(Amount) AS HighestPayment
FROM PAYMENT;

-- Query 12: Reservations with Payment Status (JOIN)
SELECT R.ReservationID, P.PaymentStatus
FROM RESERVATION R
JOIN PAYMENT P ON R.ReservationID = P.ReservationID;