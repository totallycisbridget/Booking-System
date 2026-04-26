# Booking System

A lightweight client–server booking system built in Python, featuring a REST-style API backend and a desktop GUI calendar interface for viewing and managing bookings.

## 📌 Overview

This project consists of two main components:
* **Backend API Server**
  * Built using Python’s `http.server`
  * Handles booking logic and database interaction (SQLite)
  * Exposes endpoints for retrieving calendar data, checking availability, and booking time slots

* **Desktop Client**
  * Built with `tkinter.ttk`
  * Provides an interactive calendar (week and month views)
  * Displays events from locally stored JSON data

---

## 🚀 Features

### Backend

* SQLite database with foreign key enforcement
* Export events to JSON
* Query staff availability
* Book time slots with validation
* Simple REST-like API

### Client

* Modern themed UI using `sv_ttk`
* Week and Month calendar views
* Dynamic event rendering
* Local data manager for JSON-based storage
* Sidebar navigation UI

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/totallycisbridget/Booking-System.git
cd Booking-System
```

### 2. Install dependencies

```bash
pip install pillow sv-ttk pywinstyles
```

---

## ▶️ Running the Project

### Start the Backend Server

```bash
python server.py
```

Server runs at:

```
http://localhost:8000
```

---

### Start the Client

```bash
python client.py
```

---

## 🔌 API Endpoints

### 1. Get User Calendar

```
GET /api/v1/getUserCalendar
```

Returns all events (exported as JSON).

---

### 2. Get Staff Availability

```
GET /api/v1/getStaffAvailableTime?staffID=<id>
```

**Example:**

```
/api/v1/getStaffAvailableTime?staffID=1
```

---

### 3. Book Time Slot

```
GET /api/v1/bookTimeSlot?staffID=<id>&bookDay=<day>&bookStart=<HH:MM>&bookEnd=<HH:MM>
```

**Example:**

```
/api/v1/bookTimeSlot?staffID=1&bookDay=Monday&bookStart=10:00&bookEnd=11:00
```

**Response:**

```json
{
  "success": true
}
```
---

## 🎨 UI Features

* Dark/light theme support
* Responsive calendar layout
* Event display with time formatting
* Today highlighting
* Navigation (previous / next / today)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request
---
