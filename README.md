# 🎓 Student Management System
**DBMS Mini Project | MySQL + Python (Flask)**

---

## 📌 Project Overview
A full-stack web application for managing student academic records, built with:
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript (Chart.js)

---

## 🗂️ Project Structure
```
sms/
├── app.py               ← Flask application (all routes & DB logic)
├── schema.sql           ← MySQL schema + sample data
├── requirements.txt     ← Python dependencies
├── README.md
└── templates/
    ├── base.html        ← Common sidebar layout
    ├── dashboard.html   ← Home with charts
    ├── students.html    ← Student list
    ├── student_form.html← Add/Edit student
    ├── student_view.html← Student profile
    ├── courses.html     ← Course management
    ├── course_form.html ← Add course
    ├── enrollments.html ← Course enrollment
    ├── attendance.html  ← Attendance tracking
    ├── marks.html       ← Marks & grades
    └── fees.html        ← Fee management
```

---

## 🛢️ Database Schema (ER Summary)

```
departments ──< courses
departments ──< students
students    ──< enrollments >── courses
students    ──< attendance  >── courses
students    ──< marks       >── courses
students    ──< fees
```

### Tables
| Table | Description |
|---|---|
| `departments` | Academic departments (CSE, ECE, etc.) |
| `courses` | Courses offered |
| `students` | Student master data |
| `enrollments` | Student ↔ Course mapping per semester |
| `attendance` | Daily attendance per student per course |
| `marks` | Internal + External marks, auto-grade |
| `fees` | Fee records with payment tracking |

---

## ⚙️ Setup Instructions

### 1. Install MySQL and create database
```sql
-- In MySQL CLI:
SOURCE schema.sql;
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Update DB credentials in app.py
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "YOUR_PASSWORD",   # ← change this
    "database": "student_management",
}
```

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

---

## 🔧 Features

### ✅ Student Registration
- Add, edit, delete students
- Fields: Roll No, Name, Email, Phone, DOB, Gender, Address, Department, Section, Year

### ✅ Course Enrollment
- Enroll students in courses per semester
- Prevent duplicate enrollments

### ✅ Attendance Management
- Mark Present / Absent / Late per student per course per day
- Visual attendance percentage with progress bars
- Colour-coded: Green ≥75%, Amber ≥60%, Red <60%

### ✅ Marks & Grades
- Record internal (30) + external (70) marks
- Auto-calculate total and grade (A+/A/B+/B/C/F)

### ✅ Fee Management
- Add tuition, exam, hostel, transport fees
- Mark fees as Paid with one click
- Summary of Paid / Pending / Overdue amounts

### ✅ Dashboard
- Live stats: Active Students, Courses, Departments, Pending Fees
- Bar chart: Students per Department
- Doughnut chart: Grade Distribution
- Recent admissions table

---

## 🎨 UI Features
- Dark themed responsive sidebar layout
- Modal forms (no page reload for adding records)
- Flash messages for all CRUD operations
- Badge colour coding for status fields
- Chart.js data visualizations

---

## 👥 Team Members
| Name | Roll Number | Section |
|Ashish Ranjan|AP24110010778|"AA"|
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

---

## 📅 Submission
Submitted for: **DBMS Mini Project — 2026**
Deadline: 01-04-2026 (5:00 PM)
