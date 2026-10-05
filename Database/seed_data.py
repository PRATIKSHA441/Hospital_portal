
"""
Hospital Portal - Demo Data Seeder

Generates Indian demo/master data using Faker and inserts it
into the existing hospital_portal MySQL database.

Generated:
    - 100 Patients
    - 20 Doctors
    - 30 Staff Members
    - 6 Wards
    - 120 Beds
    - Doctor Schedules
    - Portal Users
    - 1 Admin Notification

IMPORTANT:
    This is DEMO/TEST data only.

    Do not use generated credentials or fake patient data
    in a real hospital environment.

    This seeder intentionally does NOT create:
        - Appointments
        - Admissions
        - Diagnoses
        - Nurse clinical records
        - Invoices
        - Discharge records

    Those records should be created by the actual application
    workflows.
"""

import os
import random
from datetime import date, timedelta

import mysql.connector
from dotenv import load_dotenv
from faker import Faker
from werkzeug.security import generate_password_hash


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Load .env from project root
load_dotenv(os.path.join(BASE_DIR, ".env"))


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "hospital_portal")


# Indian Faker
fake = Faker("en_IN")


# Reproducible demo data
random.seed(42)
Faker.seed(42)


# ============================================================
# DATA CONFIGURATION
# ============================================================

NUMBER_OF_PATIENTS = 100
NUMBER_OF_DOCTORS = 20
NUMBER_OF_STAFF = 30

BEDS_PER_WARD = 20

# Local development/testing password only.
DEMO_PASSWORD = "Demo@123"


SPECIALISATIONS = [
    "Cardiology",
    "General Medicine",
    "Pediatrics",
    "Maternity",
    "Emergency",
]


STAFF_ROLES = [
    "Nurse",
    "Receptionist",
    "Billing",
    "HR",
    "Admin",
]


WARD_CONFIG = [
    {
        "name": "General Ward A",
        "type": "General",
        "floor": 1,
        "bed_type": "Normal",
    },
    {
        "name": "General Ward B",
        "type": "General",
        "floor": 1,
        "bed_type": "Normal",
    },
    {
        "name": "Emergency Ward",
        "type": "Emergency",
        "floor": 1,
        "bed_type": "Emergency",
    },
    {
        "name": "ICU Ward",
        "type": "ICU",
        "floor": 2,
        "bed_type": "ICU",
    },
    {
        "name": "Pediatric Ward",
        "type": "Pediatric",
        "floor": 2,
        "bed_type": "Pediatric",
    },
    {
        "name": "Maternity Ward",
        "type": "Maternity",
        "floor": 3,
        "bed_type": "Maternity",
    },
]


DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a MySQL connection using values from .env.
    """

    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def generate_indian_phone():
    """
    Generate a valid-looking Indian mobile number.
    """

    first_digit = random.choice([
        "6",
        "7",
        "8",
        "9",
    ])

    remaining = "".join(
        random.choice("0123456789")
        for _ in range(9)
    )

    return first_digit + remaining


def random_date_of_birth():
    """
    Generate a patient DOB approximately between
    5 and 80 years ago.
    """

    today = date.today()

    start_date = today - timedelta(
        days=80 * 365
    )

    end_date = today - timedelta(
        days=5 * 365
    )

    return fake.date_between(
        start_date=start_date,
        end_date=end_date,
    )


def get_gender():
    """
    Generate a demo gender value compatible with
    the patient table ENUM.
    """

    return random.choice([
        "Male",
        "Female",
    ])


def get_blood_group():
    """
    Generate a demo blood group.
    """

    return random.choice([
        "A+",
        "A-",
        "B+",
        "B-",
        "AB+",
        "AB-",
        "O+",
        "O-",
    ])


# ============================================================
# CLEAR EXISTING DEMO DATA
# ============================================================

def clear_existing_data(cursor):
    """
    Remove existing data before reseeding.

    Tables are cleared in dependency order so that
    foreign-key constraints are respected.

    WARNING:
        This removes application data from the configured
        hospital_portal database.

        Use this seeder only for development/testing.
    """

    print("\nClearing existing data...")

    tables = [
        # Child/dependent tables first
        "app_notification",
        "h_audit_log",
        "invoice",
        "admission",
        "nurse_care_log",
        "desk_history",
        "appointment",

        # Portal users depend on people/staff
        "portal_user",

        # Schedule/bed/HR tables
        "doctor_schedule",
        "bed",
        "staff_shift_hr",

        # Parent/master tables
        "ward",
        "staff_member",
        "doctor",
        "patient",
    ]

    for table in tables:
        cursor.execute(
            f"DELETE FROM `{table}`"
        )

        print(
            f"  Cleared: {table}"
        )


# ============================================================
# INSERT PATIENTS
# ============================================================

def insert_patients(cursor):
    """
    Insert demo patients.

    Matches the exact patient table schema.
    """

    print("\nCreating patients...")

    patients = []

    for _ in range(NUMBER_OF_PATIENTS):

        full_name = fake.name()

        gender = get_gender()

        phone = generate_indian_phone()

        email = fake.unique.email()

        address = fake.address().replace(
            "\n",
            ", "
        )

        dob = random_date_of_birth()

        blood_group = get_blood_group()

        emergency_name = fake.name()

        emergency_phone = generate_indian_phone()

        patients.append((
            full_name,
            dob,
            gender,
            phone,
            email,
            address,
            blood_group,
            emergency_name,
            emergency_phone,
        ))

    query = """
        INSERT INTO patient
        (
            full_name,
            date_of_birth,
            gender,
            phone,
            email,
            address,
            blood_group,
            emergency_contact_name,
            emergency_contact_phone
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.executemany(
        query,
        patients
    )

    print(
        f"  Inserted {len(patients)} patients."
    )


# ============================================================
# INSERT DOCTORS
# ============================================================

def insert_doctors(cursor):
    """
    Insert demo doctors.
    """

    print("\nCreating doctors...")

    doctors = []

    for index in range(
        1,
        NUMBER_OF_DOCTORS + 1
    ):

        full_name = (
            f"Dr. {fake.name()}"
        )

        specialisation = SPECIALISATIONS[
            (index - 1)
            % len(SPECIALISATIONS)
        ]

        phone = generate_indian_phone()

        email = (
            f"doctor{index:02d}@hospital.test"
        )

        licence_number = (
            f"MH-MED-{index:04d}"
        )

        doctors.append((
            full_name,
            specialisation,
            phone,
            email,
            licence_number,
        ))

    query = """
        INSERT INTO doctor
        (
            full_name,
            specialisation,
            phone,
            email,
            licence_number
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.executemany(
        query,
        doctors
    )

    print(
        f"  Inserted {len(doctors)} doctors."
    )


# ============================================================
# INSERT STAFF
# ============================================================

def insert_staff(cursor):
    """
    Insert demo hospital staff.

    Roles are restricted to the values defined
    by the staff_member table ENUM.
    """

    print("\nCreating staff members...")

    staff = []

    role_pattern = [
        "Nurse",
        "Nurse",
        "Nurse",
        "Receptionist",
        "Receptionist",
        "Billing",
        "HR",
        "Admin",
    ]

    for index in range(
        1,
        NUMBER_OF_STAFF + 1
    ):

        full_name = fake.name()

        role_type = role_pattern[
            (index - 1)
            % len(role_pattern)
        ]

        phone = generate_indian_phone()

        email = (
            f"staff{index:02d}@hospital.test"
        )

        staff.append((
            full_name,
            role_type,
            phone,
            email,
        ))

    query = """
        INSERT INTO staff_member
        (
            full_name,
            role_type,
            phone,
            email
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.executemany(
        query,
        staff
    )

    print(
        f"  Inserted {len(staff)} staff members."
    )


# ============================================================
# INSERT WARDS
# ============================================================

def insert_wards(cursor):
    """
    Insert hospital wards.

    Uses floor_number because that is the exact
    column name in the database schema.
    """

    print("\nCreating wards...")

    query = """
        INSERT INTO ward
        (
            ward_name,
            ward_type,
            floor_number,
            is_active
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    ward_data = []

    for ward in WARD_CONFIG:

        ward_data.append((
            ward["name"],
            ward["type"],
            ward["floor"],
            1,
        ))

    cursor.executemany(
        query,
        ward_data
    )

    print(
        f"  Inserted {len(ward_data)} wards."
    )


# ============================================================
# INSERT BEDS
# ============================================================

def insert_beds(cursor):
    """
    Insert beds for every ward.
    """

    print("\nCreating beds...")

    cursor.execute("""
        SELECT
            ward_id,
            ward_name,
            ward_type
        FROM ward
        ORDER BY ward_id
    """)

    wards = cursor.fetchall()

    query = """
        INSERT INTO bed
        (
            ward_id,
            bed_number,
            bed_type,
            status
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    beds = []

    for ward_id, ward_name, ward_type in wards:

        bed_type = "Normal"

        for config in WARD_CONFIG:

            if config["type"] == ward_type:

                bed_type = config["bed_type"]

                break

        if ward_type == "General":
            prefix = "GEN"

        elif ward_type == "Emergency":
            prefix = "EMG"

        elif ward_type == "ICU":
            prefix = "ICU"

        elif ward_type == "Pediatric":
            prefix = "PED"

        elif ward_type == "Maternity":
            prefix = "MAT"

        elif ward_type == "Surgical":
            prefix = "SUR"

        else:
            prefix = "BED"

        for bed_index in range(
            1,
            BEDS_PER_WARD + 1
        ):

            bed_number = (
                f"{prefix}-{bed_index:03d}"
            )

            beds.append((
                ward_id,
                bed_number,
                bed_type,
                "Available",
            ))

    cursor.executemany(
        query,
        beds
    )

    print(
        f"  Inserted {len(beds)} beds."
    )


# ============================================================
# INSERT DOCTOR SCHEDULES
# ============================================================

def insert_doctor_schedules(cursor):
    """
    Give every doctor a Monday-Friday schedule.

    Schedule:
        09:00 - 17:00
        30-minute appointment slots
    """

    print("\nCreating doctor schedules...")

    cursor.execute("""
        SELECT doctor_id
        FROM doctor
        ORDER BY doctor_id
    """)

    doctors = cursor.fetchall()

    schedules = []

    for (doctor_id,) in doctors:

        for day in DAYS_OF_WEEK:

            schedules.append((
                doctor_id,
                day,
                "09:00:00",
                "17:00:00",
                30,
                1,
            ))

    query = """
        INSERT INTO doctor_schedule
        (
            doctor_id,
            day_of_week,
            start_time,
            end_time,
            slot_duration,
            is_available
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.executemany(
        query,
        schedules
    )

    print(
        f"  Inserted {len(schedules)} schedule records."
    )


# ============================================================
# INSERT PORTAL USERS
# ============================================================

def insert_portal_users(cursor):
    """
    Create login accounts for:

        - 1 Admin
        - Other staff members
        - 20 Doctors
        - 100 Patients

    All accounts use the same development password.
    """

    print("\nCreating portal users...")

    users = []

    # Generate one password hash for demo accounts.
    demo_password_hash = generate_password_hash(
        DEMO_PASSWORD
    )

    # --------------------------------------------------------
    # STAFF USERS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            staff_id,
            role_type
        FROM staff_member
        ORDER BY staff_id
    """)

    staff_rows = cursor.fetchall()

    admin_created = False

    for index, (
        staff_id,
        role_type
    ) in enumerate(
        staff_rows,
        start=1
    ):

        if (
            role_type == "Admin"
            and not admin_created
        ):

            username = "admin_demo"

            users.append((
                username,
                demo_password_hash,
                "Admin",
                None,
                None,
                staff_id,
            ))

            admin_created = True

        else:

            username = (
                f"{role_type.lower()}_{index:03d}"
            )

            users.append((
                username,
                demo_password_hash,
                role_type,
                None,
                None,
                staff_id,
            ))

    # --------------------------------------------------------
    # DOCTOR USERS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT doctor_id
        FROM doctor
        ORDER BY doctor_id
    """)

    doctor_rows = cursor.fetchall()

    for index, (
        doctor_id,
    ) in enumerate(
        doctor_rows,
        start=1
    ):

        username = (
            f"doctor_{index:03d}"
        )

        users.append((
            username,
            demo_password_hash,
            "Doctor",
            doctor_id,
            None,
            None,
        ))

    # --------------------------------------------------------
    # PATIENT USERS
    # --------------------------------------------------------

    cursor.execute("""
        SELECT patient_id
        FROM patient
        ORDER BY patient_id
    """)

    patient_rows = cursor.fetchall()

    for index, (
        patient_id,
    ) in enumerate(
        patient_rows,
        start=1
    ):

        username = (
            f"patient_{index:03d}"
        )

        users.append((
            username,
            demo_password_hash,
            "Patient",
            None,
            patient_id,
            None,
        ))

    # --------------------------------------------------------
    # INSERT USERS
    # --------------------------------------------------------

    query = """
        INSERT INTO portal_user
        (
            username,
            password_hash,
            user_type,
            doctor_id,
            patient_id,
            staff_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.executemany(
        query,
        users
    )

    print(
        f"  Inserted {len(users)} portal users."
    )


# ============================================================
# CREATE INITIAL NOTIFICATION
# ============================================================

def insert_initial_notification(cursor):
    """
    Create one initial notification for the demo admin.
    """

    print("\nCreating initial notification...")

    cursor.execute("""
        SELECT user_id
        FROM portal_user
        WHERE username = 'admin_demo'
        LIMIT 1
    """)

    admin = cursor.fetchone()

    if not admin:

        print(
            "  Admin user not found. "
            "Skipping notification."
        )

        return

    admin_user_id = admin[0]

    cursor.execute("""
        INSERT INTO app_notification
        (
            recipient_user_id,
            message
        )
        VALUES
        (
            %s,
            %s
        )
    """, (
        admin_user_id,
        "Hospital Portal demo data has been initialized successfully.",
    ))

    print(
        "  Initial admin notification created."
    )


# ============================================================
# VERIFICATION
# ============================================================

def verify_data(cursor):
    """
    Print record counts after successful seeding.
    """

    print("\n" + "=" * 60)
    print("DATABASE SEED VERIFICATION")
    print("=" * 60)

    tables = [
        "patient",
        "doctor",
        "staff_member",
        "ward",
        "bed",
        "doctor_schedule",
        "portal_user",
        "app_notification",
    ]

    expected_counts = {
        "patient": NUMBER_OF_PATIENTS,
        "doctor": NUMBER_OF_DOCTORS,
        "staff_member": NUMBER_OF_STAFF,
        "ward": len(WARD_CONFIG),
        "bed": (
            len(WARD_CONFIG)
            * BEDS_PER_WARD
        ),
        "doctor_schedule": (
            NUMBER_OF_DOCTORS
            * len(DAYS_OF_WEEK)
        ),
    }

    verification_passed = True

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM `{table}`"
        )

        count = cursor.fetchone()[0]

        expected = expected_counts.get(
            table
        )

        if expected is not None:

            status = (
                "OK"
                if count == expected
                else "CHECK"
            )

            if count != expected:
                verification_passed = False

            print(
                f"{table:<25} : "
                f"{count:<5} "
                f"(expected {expected}) "
                f"[{status}]"
            )

        else:

            print(
                f"{table:<25} : "
                f"{count}"
            )

    print("=" * 60)

    if verification_passed:

        print(
            "Seed verification passed."
        )

    else:

        print(
            "Seed verification found unexpected counts."
        )

    return verification_passed


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("HOSPITAL PORTAL - INDIAN DEMO DATA SEEDER")
    print("=" * 60)

    print("\nDatabase configuration:")
    print(f"  Host     : {DB_HOST}")
    print(f"  User     : {DB_USER}")
    print(f"  Database : {DB_NAME}")

    connection = None
    cursor = None

    try:

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        print("\nConnecting to MySQL...")

        connection = get_connection()

        cursor = connection.cursor()

        print(
            "MySQL connection successful."
        )

        # ----------------------------------------------------
        # CLEAR OLD DATA
        # ----------------------------------------------------

        clear_existing_data(cursor)

        # ----------------------------------------------------
        # INSERT MASTER DATA
        # ----------------------------------------------------

        insert_patients(cursor)

        insert_doctors(cursor)

        insert_staff(cursor)

        insert_wards(cursor)

        insert_beds(cursor)

        insert_doctor_schedules(cursor)

        insert_portal_users(cursor)

        insert_initial_notification(cursor)

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        connection.commit()

        print(
            "\nAll demo data committed successfully."
        )

        # ----------------------------------------------------
        # VERIFY
        # ----------------------------------------------------

        verification_passed = verify_data(
            cursor
        )

        if verification_passed:

            print(
                "\nSeed completed successfully."
            )

        else:

            print(
                "\nSeed completed, but "
                "verification requires review."
            )

        # ----------------------------------------------------
        # DEMO LOGIN INFORMATION
        # ----------------------------------------------------

        print("\nDemo login password:")
        print(
            f"  {DEMO_PASSWORD}"
        )

        print("\nExample usernames:")

        print(
            "  admin_demo"
        )

        print(
            "  doctor_001"
        )

        print(
            "  patient_001"
        )

        print(
            "  receptionist_001"
        )

        print(
            "  nurse_001"
        )

        print(
            "\nIMPORTANT: "
            "These are development/test credentials only."
        )

    except mysql.connector.Error as error:

        print("\nMySQL ERROR:")
        print(error)

        if connection:
            connection.rollback()

        print(
            "\nTransaction rolled back."
        )

    except Exception as error:

        print("\nERROR:")
        print(error)

        if connection:
            connection.rollback()

        print(
            "\nTransaction rolled back."
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

        print(
            "\nDatabase connection closed."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
