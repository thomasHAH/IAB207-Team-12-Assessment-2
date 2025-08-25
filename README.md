Got it ✅ — I’ll draft you a **README.md** that explains everything clearly, like you’d expect on a student GitHub repo. You can drop this straight into your repo root.

---

# 📘 README.md

````markdown
# IAB207 Team 12 – Assessment 2  

## 📖 Overview
This repository contains our solution for **IAB207 Assessment 2**.  
It is a web application built using **Flask**, a lightweight Python web framework. The app provides the starting point for developing an Event Management System with features such as user accounts, events, bookings, and comments.  

The project is based on the QUT starter code provided for Assessment 2 and has been extended by our team.

---

## ⚙️ Project Structure
- **main.py** → Entry point for the application. Run this to start the Flask server.  
- **website/** → Main application package.  
  - `__init__.py` → Creates and configures the Flask app.  
  - `models.py` → Defines the database models (User, Event, Comment, Order).  
  - `routes/` (if added) → Will hold route/blueprint files for auth, events, etc.  
  - `templates/` → HTML templates rendered by Flask (uses Jinja2 + Bootstrap).  
  - `static/` → Static files (CSS, JS, images).  
- **requirements.txt** → Lists the Python dependencies needed to run the project.  
- **venv/** → Local virtual environment (not pushed to GitHub).  

---

## 🖥️ Running the Application

### 1. Clone the Repository
```bash
git clone https://github.com/thomasHAH/IAB207-Team-12-Assessment-2.git
cd IAB207-Team-12-Assessment-2
````

### 2. Create and Activate Virtual Environment

A **virtual environment (venv)** is an isolated Python environment for this project.
It keeps our dependencies separate from the system Python so every team member uses the same versions.

#### Windows (PowerShell)

```bash
python -m venv venv
venv\Scripts\activate
```

#### Mac/Linux (bash/zsh)

```bash
python3 -m venv venv
source venv/bin/activate
```

When active, your terminal prompt will show `(venv)` at the start.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, Flask-Login, Flask-WTF, Bcrypt, and other libraries.

### 4. Run the Application

```bash
python main.py
```

If successful, you’ll see:

```
 * Running on http://127.0.0.1:5000/
```

Open this link in a browser to access the app.

---

## 🚀 How It Works

* The app runs on a **Flask development server** (by default at `localhost:5000`).
* **main.py** creates the app using the factory function in `website/__init__.py`.
* **SQLAlchemy** is used to define and manage the database.
* **Flask-Login + Flask-Bcrypt** provide secure user authentication.
* **Bootstrap-Flask** is used for styling HTML templates.
* Future development will add CRUD functionality for events, user bookings, and comments.

---

## 👩‍💻 Development Workflow

1. Always **pull** the latest code before starting:

   ```bash
   git pull origin main
   ```
2. Make changes locally inside your branch/folder.
3. Run and test with:

   ```bash
   python main.py
   ```
4. Commit and **push** changes when ready:

   ```bash
   git add .
   git commit -m "Describe your changes"
   git push origin main
   ```

---

## 📝 Notes

* Only run the app with `python main.py`.
* Do **not** run individual files (e.g., `models.py`) — they use relative imports and must be run via the package.
* The `venv/` folder should not be pushed to GitHub (it is ignored via `.gitignore`).

---

```

---

👉 This README explains **what the project is, how to run it, what venv is, and that you must use `main.py`**.  

Do you want me to also add a **section on database setup** (Flask-Migrate commands for creating the SQLite DB from `models.py`) so your group knows how to initialise tables?
```
