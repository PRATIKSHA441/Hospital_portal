import os
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash

from backend.database import get_db_connection


# ---------------------------------------------------------
# Flask application
# ---------------------------------------------------------

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "super-secret-hospital-portal-key-2026"
)
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/index.html")
def index_page():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/patient.html")
def patient_page():
    return send_from_directory(FRONTEND_DIR, "patient.html")


@app.route("/doctor.html")
def doctor_page():
    return send_from_directory(FRONTEND_DIR, "doctor.html")


@app.route("/admin.html")
def admin_page():
    return send_from_directory(FRONTEND_DIR, "admin.html")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # True when deployed with HTTPS
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8  # 8 hours
)

CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
)


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "service": "Hospital Portal Backend",
        "status": "OK"
    }), 200


# ---------------------------------------------------------
# Authentication helper
# ---------------------------------------------------------

def get_current_user():
    """
    Return the authenticated user stored in the Flask session.

    Returns:
        dict | None
    """
    return session.get("user")


def login_required(func):
    """
    Require an authenticated user before accessing an endpoint.
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({
                "success": False,
                "message": "Authentication required."
            }), 401

        return func(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles):
    """
    Require authentication and one of the specified roles.
    """

    def decorator(func):

        @wraps(func)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    "success": False,
                    "message": "Authentication required."
                }), 401

            user_role = user.get("user_type")

            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "Unauthorized access."
                }), 403

            return func(*args, **kwargs)

        return decorated_function

    return decorator


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    """
    Authenticate against the existing portal_user table.

    No new user table is created.

    Passwords are verified against the existing
    Werkzeug PBKDF2-SHA256 password hashes.
    """

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                user_id,
                username,
                password_hash,
                user_type,
                doctor_id,
                patient_id,
                staff_id,
                is_active
            FROM portal_user
            WHERE username = %s
            LIMIT 1
        """

        cursor.execute(query, (username,))
        user_record = cursor.fetchone()

        # Do not reveal whether the username exists.
        if not user_record:
            return jsonify({
                "success": False,
                "message": "Invalid username or password."
            }), 401

        if not user_record["is_active"]:
            return jsonify({
                "success": False,
                "message": "This account is inactive."
            }), 403

        password_hash = user_record["password_hash"]

        if not check_password_hash(password_hash, password):
            return jsonify({
                "success": False,
                "message": "Invalid username or password."
            }), 401

        # Store identity and required profile mappings only.
        # Never store the password or password hash in session.
        session_user = {
            "user_id": user_record["user_id"],
            "username": user_record["username"],
            "user_type": user_record["user_type"],
            "doctor_id": user_record["doctor_id"],
            "patient_id": user_record["patient_id"],
            "staff_id": user_record["staff_id"]
        }

        session.clear()
        session["user"] = session_user
        session.permanent = True

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": {
                "user_id": session_user["user_id"],
                "username": session_user["username"],
                "user_type": session_user["user_type"]
            }
        }), 200

    except Exception as e:
        app.logger.exception("Login database error")

        return jsonify({
            "success": False,
            "message": "Unable to process login."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ---------------------------------------------------------
# Current session
# ---------------------------------------------------------

@app.route("/api/session", methods=["GET"])
def get_session():
    """
    Return the currently authenticated user's basic identity.
    """

    user = get_current_user()

    if not user:
        return jsonify({
            "authenticated": False
        }), 200

    return jsonify({
        "authenticated": True,
        "user": {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "user_type": user.get("user_type")
        }
    }), 200


# ---------------------------------------------------------
# Current user
# ---------------------------------------------------------

@app.route("/api/me", methods=["GET"])
@login_required
def get_current_user_profile():
    """
    Return the authenticated user's session profile.
    """

    user = get_current_user()

    return jsonify({
        "success": True,
        "user": {
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "user_type": user.get("user_type"),
            "doctor_id": user.get("doctor_id"),
            "patient_id": user.get("patient_id"),
            "staff_id": user.get("staff_id")
        }
    }), 200


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@app.route("/api/logout", methods=["POST"])
def logout():
    """
    Completely clear the authenticated Flask session.
    """

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


# ---------------------------------------------------------
# Doctor admissions
# ---------------------------------------------------------

@app.route("/api/doctor/admissions", methods=["GET"])
@role_required("Doctor")
def get_doctor_admissions():
    """
    Retrieve active admissions assigned to the authenticated doctor.

    doctor_id is always obtained from the authenticated session,
    never from a request parameter.
    """

    user = get_current_user()

    doctor_id = user.get("doctor_id")

    if not doctor_id:
        return jsonify({
            "success": False,
            "message": "Doctor profile mapping missing."
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                admission_id,
                patient_id,
                doctor_id,
                bed_id,
                admission_reason,
                status
            FROM admission
            WHERE doctor_id = %s
              AND status = 'Admitted'
            ORDER BY admission_id DESC
        """

        cursor.execute(query, (doctor_id,))
        admissions = cursor.fetchall()

        return jsonify({
            "success": True,
            "admissions": admissions
        }), 200

    except Exception:
        app.logger.exception("Doctor admissions database error")

        return jsonify({
            "success": False,
            "message": "Unable to retrieve doctor admissions."
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ---------------------------------------------------------
# Existing application startup
# ---------------------------------------------------------

if __name__ == "__main__":
    print("Hospital Portal Backend starting...")
    print("Open: http://localhost:8000")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        debug=True
    )