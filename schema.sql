-- ============================================================
--  Student Management System — MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- ────────────────────────────────────────
--  1. DEPARTMENTS
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    dept_name   VARCHAR(100) NOT NULL UNIQUE,
    dept_code   VARCHAR(10)  NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────
--  2. COURSES
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    course_id   INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    course_code VARCHAR(20)  NOT NULL UNIQUE,
    credits     INT          NOT NULL DEFAULT 3,
    dept_id     INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL
);

-- ────────────────────────────────────────
--  3. STUDENTS
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    student_id   INT AUTO_INCREMENT PRIMARY KEY,
    roll_number  VARCHAR(20)  NOT NULL UNIQUE,
    first_name   VARCHAR(60)  NOT NULL,
    last_name    VARCHAR(60)  NOT NULL,
    email        VARCHAR(120) NOT NULL UNIQUE,
    phone        VARCHAR(15),
    dob          DATE,
    gender       ENUM('Male','Female','Other'),
    address      TEXT,
    dept_id      INT,
    section      VARCHAR(10),
    year_of_study INT DEFAULT 1,
    admission_date DATE DEFAULT (CURRENT_DATE),
    status       ENUM('Active','Inactive','Graduated','Dropped') DEFAULT 'Active',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL
);

-- ────────────────────────────────────────
--  4. ENROLLMENTS
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    course_id     INT NOT NULL,
    semester      VARCHAR(20) NOT NULL,
    enrolled_on   DATE DEFAULT (CURRENT_DATE),
    UNIQUE KEY uq_enroll (student_id, course_id, semester),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
);

-- ────────────────────────────────────────
--  5. ATTENDANCE
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT  NOT NULL,
    course_id     INT  NOT NULL,
    att_date      DATE NOT NULL,
    status        ENUM('Present','Absent','Late') NOT NULL DEFAULT 'Present',
    UNIQUE KEY uq_att (student_id, course_id, att_date),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
);

-- ────────────────────────────────────────
--  6. MARKS / GRADES
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marks (
    mark_id       INT AUTO_INCREMENT PRIMARY KEY,
    student_id    INT NOT NULL,
    course_id     INT NOT NULL,
    semester      VARCHAR(20) NOT NULL,
    internal_marks DECIMAL(5,2) DEFAULT 0,
    external_marks DECIMAL(5,2) DEFAULT 0,
    total_marks    DECIMAL(5,2) GENERATED ALWAYS AS (internal_marks + external_marks) STORED,
    grade         VARCHAR(5),
    UNIQUE KEY uq_mark (student_id, course_id, semester),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES courses(course_id)  ON DELETE CASCADE
);

-- ────────────────────────────────────────
--  7. FEES
-- ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fees (
    fee_id       INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT            NOT NULL,
    fee_type     VARCHAR(60)    NOT NULL,
    amount       DECIMAL(10,2)  NOT NULL,
    due_date     DATE           NOT NULL,
    paid_date    DATE,
    status       ENUM('Pending','Paid','Overdue') DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ────────────────────────────────────────
--  SAMPLE DATA
-- ────────────────────────────────────────
INSERT INTO departments (dept_name, dept_code) VALUES
  ('Computer Science',   'CSE'),
  ('Electronics',        'ECE'),
  ('Mechanical',         'MECH'),
  ('Civil',              'CIVIL');

INSERT INTO courses (course_name, course_code, credits, dept_id) VALUES
  ('Database Management Systems', 'CS301', 4, 1),
  ('Data Structures',             'CS201', 4, 1),
  ('Operating Systems',           'CS302', 3, 1),
  ('Digital Electronics',         'EC201', 4, 2),
  ('Thermodynamics',              'ME201', 3, 3);

INSERT INTO students (roll_number, first_name, last_name, email, phone, dob, gender, dept_id, section, year_of_study) VALUES
  ('CSE2401', 'Arjun',   'Reddy',  'arjun@college.in',  '9876543210', '2005-03-15', 'Male',   1, 'A', 2),
  ('CSE2402', 'Priya',   'Sharma', 'priya@college.in',  '9876543211', '2005-07-22', 'Female', 1, 'A', 2),
  ('CSE2403', 'Rahul',   'Kumar',  'rahul@college.in',  '9876543212', '2004-11-05', 'Male',   1, 'B', 2),
  ('ECE2401', 'Sneha',   'Patel',  'sneha@college.in',  '9876543213', '2005-01-30', 'Female', 2, 'A', 2),
  ('MECH2401','Vikram',  'Singh',  'vikram@college.in', '9876543214', '2004-09-18', 'Male',   3, 'A', 2);

INSERT INTO enrollments (student_id, course_id, semester) VALUES
  (1,1,'2024-Odd'),(1,2,'2024-Odd'),(1,3,'2024-Odd'),
  (2,1,'2024-Odd'),(2,2,'2024-Odd'),
  (3,1,'2024-Odd'),(3,3,'2024-Odd'),
  (4,4,'2024-Odd'),
  (5,5,'2024-Odd');

INSERT INTO attendance (student_id, course_id, att_date, status) VALUES
  (1,1,'2026-04-21','Present'),(1,1,'2026-04-22','Present'),(1,1,'2026-04-23','Absent'),
  (2,1,'2026-04-21','Present'),(2,1,'2026-04-22','Late'),
  (3,1,'2026-04-21','Absent'),(3,1,'2026-04-22','Present');

INSERT INTO marks (student_id, course_id, semester, internal_marks, external_marks, grade) VALUES
  (1,1,'2024-Odd',28,58,'A'),(1,2,'2024-Odd',25,52,'B+'),
  (2,1,'2024-Odd',30,62,'A+'),(2,2,'2024-Odd',22,48,'B'),
  (3,1,'2024-Odd',18,40,'C');

INSERT INTO fees (student_id, fee_type, amount, due_date, status) VALUES
  (1,'Tuition Fee',45000,'2026-06-30','Pending'),
  (2,'Tuition Fee',45000,'2026-06-30','Paid'),
  (3,'Tuition Fee',45000,'2026-06-30','Overdue'),
  (4,'Tuition Fee',45000,'2026-06-30','Pending'),
  (5,'Tuition Fee',45000,'2026-06-30','Paid'),
  (1,'Exam Fee',2000,'2026-04-15','Paid'),
  (2,'Exam Fee',2000,'2026-04-15','Paid');
