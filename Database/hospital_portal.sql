
DROP DATABASE IF EXISTS hospital_portal;
CREATE DATABASE hospital_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_portal;

-- =============================================================
-- 1. CORE PARTICIPANTS (PATIENT & MEDICAL STAFF)
-- =============================================================

CREATE TABLE patient (
    patient_id              INT NOT NULL AUTO_INCREMENT,
    full_name               VARCHAR(150) NOT NULL,
    date_of_birth           DATE NOT NULL,
    gender                  ENUM('Male','Female','Other') NOT NULL,
    phone                   VARCHAR(15),
    email                   VARCHAR(150),
    address                 TEXT,
    blood_group             VARCHAR(5),
    emergency_contact_name  VARCHAR(150),
    emergency_contact_phone VARCHAR(15),
    is_active               TINYINT(1) NOT NULL DEFAULT 1,
    created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (patient_id),
    INDEX idx_patient_name (full_name),
    INDEX idx_patient_phone (phone)
);

CREATE TABLE doctor (
    doctor_id         INT NOT NULL AUTO_INCREMENT,
    full_name         VARCHAR(150) NOT NULL,
    specialisation    VARCHAR(100) NOT NULL,
    phone             VARCHAR(15),
    email             VARCHAR(150),
    licence_number    VARCHAR(50) NOT NULL,
    is_active         TINYINT(1) NOT NULL DEFAULT 1,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doctor_id),
    UNIQUE KEY uq_doctor_email (email),
    UNIQUE KEY uq_doctor_licence (licence_number),
    INDEX idx_doctor_specialisation (specialisation)
);

-- Consolidated Personnel table for Nurses, Receptionists, Billing, HR, and Admin
CREATE TABLE staff_member (
    staff_id          INT NOT NULL AUTO_INCREMENT,
    full_name         VARCHAR(150) NOT NULL,
    role_type         ENUM('Nurse', 'Receptionist', 'Billing', 'HR', 'Admin') NOT NULL,
    phone             VARCHAR(15),
    email             VARCHAR(150),
    is_active         TINYINT(1) NOT NULL DEFAULT 1,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (staff_id),
    UNIQUE KEY uq_staff_email (email)
);

-- =============================================================
-- 2. PORTAL SYSTEM, SECURITY, & ALERTS
-- =============================================================

CREATE TABLE portal_user (
    user_id       INT NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type     ENUM('Admin','Doctor','Nurse','Receptionist','Billing','HR','Patient') NOT NULL,
    doctor_id     INT DEFAULT NULL,
    patient_id    INT DEFAULT NULL,
    staff_id      INT DEFAULT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_username (username),
    CONSTRAINT fk_user_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_user_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_user_staff FOREIGN KEY (staff_id) REFERENCES staff_member (staff_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Mandatory HIPAA Security Tracking Log
CREATE TABLE h_audit_log (
    log_id          INT NOT NULL AUTO_INCREMENT,
    timestamp       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id         INT NOT NULL,
    action_performed VARCHAR(100) NOT NULL, -- e.g., 'SEARCH_BY_ID', 'DISCHARGE_PATIENT'
    patient_id      INT DEFAULT NULL,      -- ID of the patient record being handled
    query_details   TEXT,                  -- Safe operational metadata
    PRIMARY KEY (log_id),
    INDEX idx_audit_patient (patient_id),
    INDEX idx_audit_timestamp (timestamp)
);

-- App Notification Engine for Doctors & Care Teams
CREATE TABLE app_notification (
    notification_id   INT NOT NULL AUTO_INCREMENT,
    recipient_user_id INT NOT NULL,
    message           TEXT NOT NULL,
    is_read           TINYINT(1) NOT NULL DEFAULT 0,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    INDEX idx_notif_recipient (recipient_user_id, is_read)
);

-- =============================================================
-- 3. CLINICAL MANAGEMENT (AI WORKFLOW INTEGRATED)
-- =============================================================

CREATE TABLE appointment (
    appointment_id         INT NOT NULL AUTO_INCREMENT,
    patient_id             INT NOT NULL,
    doctor_id              INT NOT NULL,
    appointment_date       DATE NOT NULL,
    appointment_time       TIME NOT NULL,
    reason                 TEXT,
    symptoms               TEXT,
    ai_specialisation      VARCHAR(100),
    ai_recommendation      TEXT,          -- Diagnostic suggestions from Groq Agent
    ai_allocated_slot_time TIME DEFAULT NULL, -- Auto-selected available slot
    assigned_by_ai         TINYINT(1) DEFAULT 0,
    ai_history_summary     TEXT,          -- Summarized profile for Doctor panel
    diagnosis              TEXT,
    doctor_notes           TEXT,
    status                 ENUM('Scheduled','Confirmed','Completed','Cancelled','No Show') NOT NULL DEFAULT 'Scheduled',
    created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (appointment_id),
    CONSTRAINT fk_appointment_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_appointment_patient (patient_id),
    INDEX idx_appointment_doctor (doctor_id),
    INDEX idx_appointment_date (appointment_date)
);

CREATE TABLE nurse_care_log (
    log_id            INT NOT NULL AUTO_INCREMENT,
    patient_id        INT NOT NULL,
    nurse_id          INT NOT NULL,
    blood_pressure    VARCHAR(20),
    temperature_c     DECIMAL(4,2),
    pulse_rate        INT,
    care_notes        TEXT,                -- Managed by automated Nurse form
    logged_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    CONSTRAINT fk_nurse_log_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_nurse_log_staff FOREIGN KEY (nurse_id) REFERENCES staff_member (staff_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- =============================================================
-- 4. ADMISSIONS, BED INVENTORY, & BILLING LEDGER
-- =============================================================

CREATE TABLE ward (
    ward_id       INT NOT NULL AUTO_INCREMENT,
    ward_name     VARCHAR(100) NOT NULL,
    ward_type     ENUM('General','Emergency','ICU','Pediatric','Maternity','Surgical') NOT NULL,
    floor_number  INT,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ward_id),
    UNIQUE KEY uq_ward_name (ward_name)
);

CREATE TABLE bed (
    bed_id        INT NOT NULL AUTO_INCREMENT,
    ward_id       INT NOT NULL,
    bed_number    VARCHAR(20) NOT NULL,
    bed_type      ENUM('Normal','ICU','Emergency','Pediatric','Maternity') NOT NULL,
    status        ENUM('Available','Occupied','Reserved','Maintenance') NOT NULL DEFAULT 'Available',
    PRIMARY KEY (bed_id),
    CONSTRAINT fk_bed_ward FOREIGN KEY (ward_id) REFERENCES ward (ward_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE KEY uq_ward_bed (ward_id, bed_number),
    INDEX idx_bed_status (status)
);

CREATE TABLE invoice (
    invoice_id        INT NOT NULL AUTO_INCREMENT,
    patient_id        INT NOT NULL,
    appointment_id    INT DEFAULT NULL,
    total_amount      DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    insurance_claim   ENUM('None', 'Filed', 'Approved', 'Rejected') NOT NULL DEFAULT 'None',
    payment_status    ENUM('Paid', 'Unpaid', 'Partially Paid') NOT NULL DEFAULT 'Unpaid',
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (invoice_id),
    CONSTRAINT fk_invoice_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_invoice_apt FOREIGN KEY (appointment_id) REFERENCES appointment (appointment_id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_invoice_patient (patient_id),
    INDEX idx_invoice_status (payment_status)
);

CREATE TABLE admission (
    admission_id         INT NOT NULL AUTO_INCREMENT,
    patient_id           INT NOT NULL,
    appointment_id       INT DEFAULT NULL,
    doctor_id            INT NOT NULL,
    bed_id               INT DEFAULT NULL,
    admission_date       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expected_discharge   DATE DEFAULT NULL,
    admission_reason     TEXT,
    diagnosis            TEXT,
    status               ENUM('Admitted','Under Treatment','Treatment Completed','Discharge Pending','Discharged','Cancelled') NOT NULL DEFAULT 'Admitted',
    doctor_approved      TINYINT(1) NOT NULL DEFAULT 0,
    generated_invoice_id INT DEFAULT NULL, -- Bound immediately upon automated discharge
    created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (admission_id),
    CONSTRAINT fk_admission_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT fk_admission_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT fk_admission_bed FOREIGN KEY (bed_id) REFERENCES bed (bed_id) ON DELETE SET NULL ON UPDATE CASCADE,
CONSTRAINT fk_admission_invoice FOREIGN KEY (generated_invoice_id) REFERENCES invoice (invoice_id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE TABLE desk_history (
history_id        INT NOT NULL AUTO_INCREMENT,
patient_id        INT NOT NULL,
receptionist_id   INT NOT NULL,
visit_type        ENUM('Appointment Check-In', 'Walk-In', 'General Inquiry') NOT NULL,
checkin_time      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
notes             VARCHAR(255),
PRIMARY KEY (history_id),
CONSTRAINT fk_desk_patient FOREIGN KEY (patient_id) REFERENCES patient (patient_id) ON DELETE RESTRICT ON UPDATE CASCADE,
CONSTRAINT fk_desk_staff FOREIGN KEY (receptionist_id) REFERENCES staff_member (staff_id) ON DELETE RESTRICT ON UPDATE CASCADE,
INDEX idx_desk_patient (patient_id)
);
-- =============================================================
-- 5. HR MANAGEMENT & WORKING SCHEDULES
-- =============================================================
CREATE TABLE doctor_schedule (
schedule_id    INT NOT NULL AUTO_INCREMENT,
doctor_id      INT NOT NULL,
day_of_week    ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
start_time     TIME NOT NULL,
end_time       TIME NOT NULL,
slot_duration  INT NOT NULL DEFAULT 30,
is_available   TINYINT(1) NOT NULL DEFAULT 1,
PRIMARY KEY (schedule_id),
CONSTRAINT fk_schedule_doctor FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id) ON DELETE CASCADE ON UPDATE CASCADE,
INDEX idx_schedule_doctor_day (doctor_id, day_of_week)
);
CREATE TABLE staff_shift_hr (
shift_id       INT NOT NULL AUTO_INCREMENT,
staff_id       INT NOT NULL,
shift_date     DATE NOT NULL,
start_time     TIME NOT NULL,
end_time       TIME NOT NULL,
payroll_hours  DECIMAL(5,2) DEFAULT 0.00,
PRIMARY KEY (shift_id),
CONSTRAINT fk_hr_staff_shift FOREIGN KEY (staff_id) REFERENCES staff_member (staff_id) ON DELETE CASCADE ON UPDATE CASCADE,
UNIQUE KEY uq_staff_shift (staff_id, shift_date)
);
