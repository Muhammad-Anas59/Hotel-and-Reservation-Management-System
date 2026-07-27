-- =============================================
-- HOTEL MANAGEMENT SYSTEM (PostgreSQL version)
-- =============================================

-- =============================================
-- DDL: TABLE CREATION
-- =============================================

CREATE TABLE hotel (
  "HotelID" SERIAL PRIMARY KEY,
  "HotelName" VARCHAR(100) NOT NULL,
  "HotelAddress" VARCHAR(255) NOT NULL,
  "HotelPhone" VARCHAR(20) UNIQUE
);

CREATE TABLE branch (
  "BranchID" SERIAL PRIMARY KEY,
  "HotelID" INT NOT NULL,
  "BranchName" VARCHAR(100) NOT NULL,
  "BranchAddress" VARCHAR(255) NOT NULL,
  "BranchPhone" VARCHAR(20) UNIQUE
);

CREATE TABLE roomtype (
  "RoomTypeID" SERIAL PRIMARY KEY,
  "TypeName" VARCHAR(50) NOT NULL,
  "Capacity" INT NOT NULL CHECK ("Capacity" > 0),
  "PricePerNight" DECIMAL(10,2) NOT NULL CHECK ("PricePerNight" > 0)
);

CREATE TABLE room (
  "RoomID" SERIAL PRIMARY KEY,
  "BranchID" INT NOT NULL,
  "RoomTypeID" INT NOT NULL,
  "RoomNumber" VARCHAR(10) NOT NULL,
  "FloorNumber" INT NOT NULL,
  "Status" VARCHAR(20) DEFAULT 'Available' CHECK ("Status" IN ('Available','Occupied','Maintenance'))
);

CREATE TABLE customer (
  "CustomerID" SERIAL PRIMARY KEY,
  "FirstName" VARCHAR(50) NOT NULL,
  "LastName" VARCHAR(50) NOT NULL,
  "CNIC_Passport" VARCHAR(20) UNIQUE NOT NULL,
  "Email" VARCHAR(100) UNIQUE,
  "Phone" VARCHAR(20) NOT NULL,
  "Address" VARCHAR(255)
);

CREATE TABLE employee (
  "EmployeeID" SERIAL PRIMARY KEY,
  "BranchID" INT NOT NULL,
  "FirstName" VARCHAR(50) NOT NULL,
  "LastName" VARCHAR(50) NOT NULL,
  "Position" VARCHAR(50) NOT NULL,
  "Salary" DECIMAL(10,2) CHECK ("Salary" > 0),
  "Phone" VARCHAR(20)
);

CREATE TABLE reservation (
  "ReservationID" SERIAL PRIMARY KEY,
  "CustomerID" INT NOT NULL,
  "RoomID" INT NOT NULL,
  "CheckInDate" DATE NOT NULL,
  "CheckOutDate" DATE NOT NULL,
  "ReservationDate" DATE NOT NULL,
  "NumberOfGuests" INT CHECK ("NumberOfGuests" > 0),
  "ReservationStatus" VARCHAR(20) DEFAULT 'Pending'
    CHECK ("ReservationStatus" IN ('Pending','Confirmed','Cancelled','Completed'))
);

CREATE TABLE payment (
  "PaymentID" SERIAL PRIMARY KEY,
  "ReservationID" INT NOT NULL,
  "Amount" DECIMAL(10,2) CHECK ("Amount" > 0),
  "PaymentDate" DATE NOT NULL,
  "PaymentMethod" VARCHAR(30),
  "PaymentStatus" VARCHAR(20) DEFAULT 'Pending'
    CHECK ("PaymentStatus" IN ('Pending','Paid','Refunded'))
);

CREATE TABLE service (
  "ServiceID" SERIAL PRIMARY KEY,
  "ServiceName" VARCHAR(100) NOT NULL,
  "ServicePrice" DECIMAL(10,2) CHECK ("ServicePrice" > 0)
);

CREATE TABLE service_booking (
  "ServiceBookingID" SERIAL PRIMARY KEY,
  "ReservationID" INT NOT NULL,
  "ServiceID" INT NOT NULL,
  "Quantity" INT CHECK ("Quantity" > 0),
  "ServiceDate" DATE NOT NULL
);

-- =============================================
-- FOREIGN KEY RELATIONSHIPS
-- =============================================

ALTER TABLE branch ADD FOREIGN KEY ("HotelID") REFERENCES hotel("HotelID");
ALTER TABLE room ADD FOREIGN KEY ("BranchID") REFERENCES branch("BranchID");
ALTER TABLE room ADD FOREIGN KEY ("RoomTypeID") REFERENCES roomtype("RoomTypeID");
ALTER TABLE employee ADD FOREIGN KEY ("BranchID") REFERENCES branch("BranchID");
ALTER TABLE reservation ADD FOREIGN KEY ("CustomerID") REFERENCES customer("CustomerID");
ALTER TABLE reservation ADD FOREIGN KEY ("RoomID") REFERENCES room("RoomID");
ALTER TABLE payment ADD FOREIGN KEY ("ReservationID") REFERENCES reservation("ReservationID");
ALTER TABLE service_booking ADD FOREIGN KEY ("ReservationID") REFERENCES reservation("ReservationID");
ALTER TABLE service_booking ADD FOREIGN KEY ("ServiceID") REFERENCES service("ServiceID");

-- =============================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================

CREATE INDEX idx_reservation_customer ON reservation("CustomerID");
CREATE INDEX idx_reservation_room ON reservation("RoomID");
CREATE INDEX idx_room_branch ON room("BranchID");
CREATE INDEX idx_payment_reservation ON payment("ReservationID");

-- =============================================
-- DML: DATA INSERTION
-- =============================================

INSERT INTO hotel VALUES (1,'Pearl Hotels','Lahore, Pakistan','0421111111');
INSERT INTO hotel VALUES (2,'Royal Stay Hotels','Islamabad, Pakistan','0512222222');

INSERT INTO branch VALUES (101,1,'Pearl Gulberg','Gulberg Lahore','0421234567');
INSERT INTO branch VALUES (102,1,'Pearl DHA','DHA Lahore','0422345678');
INSERT INTO branch VALUES (201,2,'Royal Blue Area','Blue Area Islamabad','0513456789');
INSERT INTO branch VALUES (202,2,'Royal F-10','F-10 Islamabad','0514567890');

INSERT INTO roomtype VALUES (1,'Single',1,5000);
INSERT INTO roomtype VALUES (2,'Double',2,8000);
INSERT INTO roomtype VALUES (3,'Deluxe',3,12000);
INSERT INTO roomtype VALUES (4,'Suite',4,20000);

INSERT INTO room VALUES (1,101,1,'101',1,'Available');
INSERT INTO room VALUES (2,101,2,'102',1,'Occupied');
INSERT INTO room VALUES (3,101,3,'201',2,'Available');
INSERT INTO room VALUES (4,102,1,'103',1,'Maintenance');
INSERT INTO room VALUES (5,102,2,'104',1,'Available');
INSERT INTO room VALUES (6,102,4,'301',3,'Occupied');
INSERT INTO room VALUES (7,201,1,'105',1,'Available');
INSERT INTO room VALUES (8,201,3,'202',2,'Occupied');
INSERT INTO room VALUES (9,201,4,'302',3,'Available');
INSERT INTO room VALUES (10,202,2,'106',1,'Available');
INSERT INTO room VALUES (11,202,3,'203',2,'Occupied');
INSERT INTO room VALUES (12,202,4,'303',3,'Available');

INSERT INTO customer VALUES (1,'Ali','Khan','35201-1111111-1','ali@gmail.com','03001111111','Lahore');
INSERT INTO customer VALUES (2,'Ahmed','Raza','35201-2222222-2','ahmed@gmail.com','03002222222','Islamabad');
INSERT INTO customer VALUES (3,'Usman','Malik','35201-3333333-3','usman@gmail.com','03003333333','Karachi');
INSERT INTO customer VALUES (4,'Hassan','Shah','35201-4444444-4','hassan@gmail.com','03004444444','Faisalabad');
INSERT INTO customer VALUES (5,'Bilal','Akram','35201-5555555-5','bilal@gmail.com','03005555555','Multan');
INSERT INTO customer VALUES (6,'Hamza','Nawaz','35201-6666666-6','hamza@gmail.com','03006666666','Sialkot');
INSERT INTO customer VALUES (7,'Saad','Ashraf','35201-7777777-7','saad@gmail.com','03007777777','Lahore');
INSERT INTO customer VALUES (8,'Anas','Javed','35201-8888888-8','anas@gmail.com','03008888888','Gujranwala');

INSERT INTO employee VALUES (1,101,'Ayesha','Malik','Manager',90000,'03111111111');
INSERT INTO employee VALUES (2,101,'Sara','Khan','Receptionist',50000,'03112222222');
INSERT INTO employee VALUES (3,102,'Zain','Ali','Manager',90000,'03113333333');
INSERT INTO employee VALUES (4,201,'Umair','Raza','Receptionist',50000,'03114444444');
INSERT INTO employee VALUES (5,202,'Fatima','Noor','Manager',95000,'03115555555');
INSERT INTO employee VALUES (6,202,'Hina','Aslam','Accountant',60000,'03116666666');

INSERT INTO reservation VALUES (1,1,2,'2026-06-10','2026-06-12','2026-06-01',2,'Confirmed');
INSERT INTO reservation VALUES (2,2,6,'2026-06-11','2026-06-14','2026-06-02',2,'Confirmed');
INSERT INTO reservation VALUES (3,3,8,'2026-06-15','2026-06-18','2026-06-03',3,'Pending');
INSERT INTO reservation VALUES (4,4,11,'2026-06-16','2026-06-20','2026-06-04',2,'Confirmed');
INSERT INTO reservation VALUES (5,5,3,'2026-06-21','2026-06-24','2026-06-05',2,'Completed');
INSERT INTO reservation VALUES (6,6,9,'2026-06-22','2026-06-25','2026-06-06',4,'Confirmed');

INSERT INTO payment VALUES (1,1,16000,'2026-06-01','Card','Paid');
INSERT INTO payment VALUES (2,2,24000,'2026-06-02','Cash','Paid');
INSERT INTO payment VALUES (3,3,36000,'2026-06-03','Card','Pending');
INSERT INTO payment VALUES (4,4,32000,'2026-06-04','Online','Paid');
INSERT INTO payment VALUES (5,5,36000,'2026-06-05','Cash','Paid');
INSERT INTO payment VALUES (6,6,60000,'2026-06-06','Card','Paid');

INSERT INTO service VALUES (1,'Laundry',1000);
INSERT INTO service VALUES (2,'Spa',3000);
INSERT INTO service VALUES (3,'Room Service',1500);
INSERT INTO service VALUES (4,'Airport Pickup',5000);

INSERT INTO service_booking VALUES (1,1,1,2,'2026-06-10');
INSERT INTO service_booking VALUES (2,1,3,1,'2026-06-10');
INSERT INTO service_booking VALUES (3,2,2,1,'2026-06-11');
INSERT INTO service_booking VALUES (4,4,4,1,'2026-06-16');

-- =============================================
-- RESET SEQUENCE COUNTERS
-- (so the next real record created by the app doesn't collide with sample data IDs)
-- =============================================

SELECT setval(pg_get_serial_sequence('hotel', 'HotelID'), (SELECT MAX("HotelID") FROM hotel));
SELECT setval(pg_get_serial_sequence('branch', 'BranchID'), (SELECT MAX("BranchID") FROM branch));
SELECT setval(pg_get_serial_sequence('roomtype', 'RoomTypeID'), (SELECT MAX("RoomTypeID") FROM roomtype));
SELECT setval(pg_get_serial_sequence('room', 'RoomID'), (SELECT MAX("RoomID") FROM room));
SELECT setval(pg_get_serial_sequence('customer', 'CustomerID'), (SELECT MAX("CustomerID") FROM customer));
SELECT setval(pg_get_serial_sequence('employee', 'EmployeeID'), (SELECT MAX("EmployeeID") FROM employee));
SELECT setval(pg_get_serial_sequence('reservation', 'ReservationID'), (SELECT MAX("ReservationID") FROM reservation));
SELECT setval(pg_get_serial_sequence('payment', 'PaymentID'), (SELECT MAX("PaymentID") FROM payment));
SELECT setval(pg_get_serial_sequence('service', 'ServiceID'), (SELECT MAX("ServiceID") FROM service));
SELECT setval(pg_get_serial_sequence('service_booking', 'ServiceBookingID'), (SELECT MAX("ServiceBookingID") FROM service_booking));