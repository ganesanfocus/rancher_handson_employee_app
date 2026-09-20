import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-this-secret"
)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "defaultdb")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Employee(db.Model):
    __tablename__ = "employees"

    emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.route("/")
def index():
    employees = Employee.query.order_by(
        Employee.emp_id.desc()
    ).all()

    return render_template(
        "index.html",
        employees=employees
    )


# --------------------------------------------------
# Create Table
# --------------------------------------------------

@app.route("/create-table")
def create_table():
    try:
        db.create_all()
        return "Employees table created successfully!"
    except Exception as e:
        return f"Error creating table: {str(e)}"


# --------------------------------------------------
# Register
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")

        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        existing_employee = Employee.query.filter_by(
            email=email
        ).first()

        if existing_employee:
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        employee = Employee(
            fullname=fullname,
            email=email,
            password=hashed_password
        )

        db.session.add(employee)
        db.session.commit()

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# --------------------------------------------------
# Login
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        employee = Employee.query.filter_by(
            email=email
        ).first()

        if employee and check_password_hash(
            employee.password,
            password
        ):

            session["emp_id"] = employee.emp_id
            session["fullname"] = employee.fullname

            flash("Login successful.", "success")

            return redirect(url_for("index"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("login"))


# --------------------------------------------------
# Employee CRUD
# --------------------------------------------------

@app.route("/employees")
def employees():

    employee_list = Employee.query.order_by(
        Employee.emp_id.desc()
    ).all()

    return render_template(
        "employees.html",
        employees=employee_list
    )


# CREATE
@app.route("/employees/create", methods=["POST"])
def create_employee():

    fullname = request.form.get("fullname")
    email = request.form.get("email")
    password = request.form.get("password")

    if not fullname or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for("employees"))

    existing_employee = Employee.query.filter_by(
        email=email
    ).first()

    if existing_employee:
        flash("Email already exists.", "warning")
        return redirect(url_for("employees"))

    employee = Employee(
        fullname=fullname,
        email=email,
        password=generate_password_hash(password)
    )

    db.session.add(employee)
    db.session.commit()

    flash("Employee created successfully.", "success")

    return redirect(url_for("employees"))


# UPDATE
@app.route("/employees/edit/<int:emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):

    employee = Employee.query.get_or_404(emp_id)

    if request.method == "POST":

        employee.fullname = request.form.get("fullname")
        employee.email = request.form.get("email")

        password = request.form.get("password")

        if password:
            employee.password = generate_password_hash(password)

        employee.updated_at = datetime.utcnow()

        db.session.commit()

        flash("Employee updated successfully.", "success")

        return redirect(url_for("employees"))

    return render_template(
        "edit_employee.html",
        employee=employee
    )


# DELETE
@app.route("/employees/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):

    employee = Employee.query.get_or_404(emp_id)

    db.session.delete(employee)
    db.session.commit()

    flash("Employee deleted successfully.", "success")

    return redirect(url_for("employees"))


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.route("/health")
def health():

    try:
        db.session.execute(db.text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }, 200

    except Exception as e:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 500


# --------------------------------------------------
# Application
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )