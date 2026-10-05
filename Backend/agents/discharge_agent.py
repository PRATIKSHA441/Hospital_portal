from backend.database import db_execute


class DischargeAgent:
    def process_discharge(self, admission_id, final_diagnosis, invoice_id):
        """
        Completes the discharge workflow:
        - verifies the admission
        - records doctor approval/discharge
        - releases the allocated bed
        - sends notification to the correct doctor portal user
        """

        # 1. Retrieve admission context
        adm_query = """
            SELECT bed_id, doctor_id, patient_id
            FROM admission
            WHERE admission_id = %s
        """

        adm_record = db_execute(
            adm_query,
            (admission_id,),
            fetch=True
        )

        if not adm_record:
            return {
                "status": "Failed",
                "message": "Admission tracker log entry profile not found."
            }

        bed_id = adm_record[0]["bed_id"]
        doctor_id = adm_record[0]["doctor_id"]
        patient_id = adm_record[0]["patient_id"]

        # 2. Find the authenticated doctor portal account
        doctor_user_query = """
            SELECT user_id
            FROM portal_user
            WHERE doctor_id = %s
              AND user_type = 'Doctor'
              AND is_active = 1
            LIMIT 1
        """

        doctor_user = db_execute(
            doctor_user_query,
            (doctor_id,),
            fetch=True
        )

        if not doctor_user:
            return {
                "status": "Failed",
                "message": "Active portal account for the attending doctor was not found."
            }

        doctor_user_id = doctor_user[0]["user_id"]

        # 3. Update admission status
        discharge_query = """
            UPDATE admission
            SET
                status = 'Discharged',
                diagnosis = %s,
                doctor_approved = 1,
                expected_discharge = CURDATE(),
                generated_invoice_id = %s
            WHERE admission_id = %s
        """

        db_execute(
            discharge_query,
            (
                final_diagnosis,
                invoice_id,
                admission_id
            ),
            commit=True
        )

        # 4. Release the allocated bed
        if bed_id:
            db_execute(
                """
                UPDATE bed
                SET status = 'Available'
                WHERE bed_id = %s
                """,
                (bed_id,),
                commit=True
            )

        # 5. Notify the correct doctor portal account
        notif_msg = (
            f"Patient ID {patient_id} has been safely discharged. "
            f"Bed ID {bed_id} is now recycled back to active inventory."
        )

        db_execute(
            """
            INSERT INTO app_notification
                (recipient_user_id, message)
            VALUES
                (%s, %s)
            """,
            (
                doctor_user_id,
                notif_msg
            ),
            commit=True
        )

        return {
            "status": "Success",
            "message": "Discharge transaction paths completed successfully."
        }