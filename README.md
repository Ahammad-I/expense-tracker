# 💸 Expense Tracker (Full Stack)

A simple yet production-ready **Expense Tracker** built with:

* ⚙️ Backend: Django + Django REST Framework
* 🎨 Frontend: React (Vite)
* 💾 Database: SQLite
* 🌐 API-first architecture

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
* CORS-enabled for frontend-backend communication

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

### 3. Install required packages (if missing)

```bash
pip install python-decouple whitenoise django-cors-headers django-filter
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start server

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
VITE_API_BASE_URL=http://127.0.0.1:8000
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

**Headers:**

```
Content-Type: application/json
Idempotency-Key: <optional-uuid>
```

**Body:**

```json
{
  "amount": "450.00",
  "category": "food",
  "description": "Dinner",
  "date": "2025-04-20"
}
```

---

### 📥 Get Expenses

```
GET /api/v1/expenses/
```

### 🔍 Filter by category

```
GET /api/v1/expenses/?category=food
```

### 🔃 Sort by date

```
GET /api/v1/expenses/?sort=date_desc
GET /api/v1/expenses/?sort=date_asc
```

### 📅 Filter by date range

```
GET /api/v1/expenses/?date_from=2025-04-01&date_to=2025-04-30
```

---

### 📊 Response Example

```json
{
  "count": 2,
  "total": "1650.00",
  "results": [...]
}
```

---

## ⚠️ Validation & Edge Cases (VERY IMPORTANT)

### 🧪 Form Validation (Frontend + Backend)

| Case                   | Expected Behavior                    |
| ---------------------- | ------------------------------------ |
| Empty form             | ❌ Error: Required fields             |
| Negative amount        | ❌ "Amount must be greater than zero" |
| Too many decimals      | ❌ Max 2 decimal places               |
| Empty description      | ❌ Cannot be blank                    |
| Invalid date format    | ❌ Must be YYYY-MM-DD                 |
| Future date (> 1 year) | ❌ Rejected                           |
| Missing category       | ❌ Required                           |

---

### 🔐 API Edge Cases

#### 1. Duplicate Requests (Idempotency)

* Same `Idempotency-Key` → returns same response
* Prevents duplicate DB entries

---

#### 2. Unsupported Media Type (415)

Occurs when:

* Missing `Content-Type: application/json`
* Invalid request body

---

#### 3. Empty Payload

* Returns structured validation error

---

#### 4. Large Numbers / Precision

* Uses Decimal (no floating point issues)

---

#### 5. Invalid Query Params

* Unknown filters ignored safely

---

#### 6. Sorting Edge Case

* Default: `date_desc`
* Invalid sort → fallback to default

---

#### 7. Total Calculation

* Always matches filtered dataset
* Returned as string to preserve precision

---

## 🧠 Frontend Behavior

### ✅ Handles:

* Instant validation (before API call)
* Backend error parsing (`err.details`)
* Filter + sort state sync
* Total updates dynamically
* Form reset after submit

---

### ❌ Prevents:

* Empty API requests
* Invalid submissions
* Duplicate entries (via idempotency)

---

## 🐞 Common Issues & Fixes

### 1. White Screen

* Cause: JS error / missing exports
* Fix: Check browser console (F12)

---

### 2. 415 Unsupported Media Type

* Fix: Ensure:

```js
headers: { 'Content-Type': 'application/json' }
```

---

### 3. CORS Error

* Add in Django:

```
corsheaders
```

---

### 4. API Not Connecting

* Check `.env`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

### 5. New Expense Not Showing

* Ensure:

```js
await loadExpenses()
```

---

## 📦 Tech Stack

* Django
* Django REST Framework
* React (Vite)
* SQLite
* Python Decouple
* WhiteNoise

---

## ✨ Future Improvements

* Authentication (JWT)
* Pagination
* Charts (monthly analytics)
* Export to CSV
* Dark mode UI
* Mobile responsive design

---

## 👨‍💻 Author

**Ahammad Hussain**

* IIT Jodhpur Graduate
* Full Stack Developer

---

## 📄 License

This project is open-source and free to use.
