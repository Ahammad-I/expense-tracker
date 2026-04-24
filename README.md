 

# 💸 Expense Tracker (Full Stack)

A simple yet production-ready **Expense Tracker** built with:

* ⚙️ Backend: Django + Django REST Framework
* 🎨 Frontend: React (Vite)
* 💾 Database: SQLite (local) / PostgreSQL (production)
* 🌐 API-first architecture

---

## 🚀 Live Production

### 🌐 Frontend (Vercel)

```
https://expense-tracker-jet-six-44.vercel.app
```

### ⚙️ Backend API (Render)

```
https://expense-tracker-i47m.onrender.com/api/v1/expenses/
```

---

## 🚀 Features

### ✅ Core Functionality

* Add new expenses
* View all expenses
* Filter expenses by category
* Sort expenses by date (Newest / Oldest)
* View total expenses for current filtered list

---

### ✅ Advanced Features

* Idempotent API (prevents duplicate submissions)
* Backend validation (robust + secure)
* Frontend validation (instant feedback)
* Clean error handling (structured API errors)
* Decimal-safe financial calculations
* CORS-enabled frontend-backend communication

---

## 🏗️ Project Structure

```
expense-tracker/
│
├── backend/
│   ├── config/
│   ├── expenses/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── expenses.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env
│
└── README.md
```

---

## ⚙️ Backend Setup (Django)

### 1. Create & activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Start server

```bash
python manage.py runserver
```

👉 Backend runs at:

```
http://127.0.0.1:8000
```

---

## 🎨 Frontend Setup (React + Vite)

### 1. Navigate to frontend

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Create `.env` file

```
VITE_API_BASE_URL=https://expense-tracker-i47m.onrender.com
```

### 4. Run frontend

```bash
npm run dev
```

👉 Frontend runs at:

```
http://localhost:3000
```

---

## 🔌 API Endpoints

### ➕ Create Expense

```
POST /api/v1/expenses/
```

### 📥 Get Expenses

```
GET /api/v1/expenses/
```

### 🔍 Filter

```
GET /api/v1/expenses/?category=food
```

### 🔃 Sort

```
GET /api/v1/expenses/?sort=date_desc
```

---

## 📊 Example Response

```json
{
  "count": 2,
  "total": "1650.00",
  "results": []
}
```

---

## 🧠 Tech Stack

* Django
* Django REST Framework
* React (Vite)
* PostgreSQL (Render)
* SQLite (local)
* WhiteNoise
* CORS Headers

---

## ✨ Future Improvements

* JWT Authentication
* Monthly analytics dashboard
* Charts (Recharts)
* Export CSV
* Mobile responsive UI

---

## 👨‍💻 Author

**Ahammad Hussain**

* IIT Jodhpur Graduate
* Full Stack Developer
 

Just tell me 👍
