# University Bus Management & Inspection System (UBMIS)

A comprehensive web-based platform designed to streamline university transport operations, including fleet management, route scheduling, seat booking, and vehicle inspection.

## Features

### 🚌 Fleet Management
- **Bus & Driver Database**: Manage detailed profiles for buses and drivers.
- **Assignment**: Easily assign drivers to specific buses.
- **Maintenance Tracking**: Log and track vehicle maintenance requests.

### 📍 Routes & Scheduling
- **Route Management**: Define routes with unlimited ordered stops.
- **Dynamic Scheduling**: Create recurring schedules with departure times and vehicle assignments.
- **Trip Generation**: Automatically generates daily trips based on schedules.

### 🎫 Seat Booking System
- **Student Dashboard**: Students can view active trips and book seats.
- **Real-time Seating**: Interactively select seats (Seats 1-40) or join a Standby list.
- **Booking Window**: Global booking start/end times managed by Admin.

### 🗺️ Live Tracking
- **Interactive Maps**: View bus locations in real-time.
- **Driver Dashboard**: Drivers can broadcast their location via GPS.
- **Follow Mode**: Maps auto-center on the active bus.

### 🛠️ Inspection Module
- **Digital Checklists**: Inspectors can perform daily/monthly vehicle checks.
- **Photo Evidence**: Upload images of reported issues.
- **Status Reporting**: Track pass/fail status and comments.

## Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL Server

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Univeersity-bus-management-system
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database:**
   - Create a MySQL database named `ubmis_db`.
   - Update `ubmis_project/settings.py` with your database credentials.

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate Demo Data (Optional):**
   ```bash
   python populate_data.py
   ```
   This creates:
   - Superuser: `admin` / `admin123`
   - Drivers: `driver1`, `driver2`, `driver3` (password: `password123`)
   - Buses, Routes, and Schedules.

8. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## User Roles & Access

- **Admin**: Full access to dashboard stats, fleet, routes, users, and settings.
- **Student**: Book seats, view history, track buses.
- **Driver**: View assigned duties, start trips, broadcast location.
- **Inspector**: Perform vehicle inspections.

## Technology Stack
- **Backend**: Django 4.x
- **Database**: MySQL
- **Frontend**: Bootstrap 5, Jinja2 Templates
- **Maps**: Leaflet.js / OpenStreetMap

---
*Developed for University Transport Department*
