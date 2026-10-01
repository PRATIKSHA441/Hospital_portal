from backend.database import db_execute

class DischargeAgent:
    def process_discharge(self, admission_id, final_diagnosis, invoice_id):
        """Fulfills the entire discharge workflow: updates the admission status, releases the bed, and sends a notification."""
        # Retrieve the allocated bed metadata bound to this admission context
        adm_query = "SELECT bed_id, doctor_id, patient_id FROM admission WHERE admission_id = %s"
        adm_record = db_execute(adm_query, (admission_id,), fetch=True)
        
        if not adm_record:
            return {"status": "Failed", "message": "Admission tracker log entry profile not found."}
            
        bed_id = adm_record[0]['bed_id']
        doctor_id = adm_record[0]['doctor_id']
        patient_id = adm_record[0]['patient_id']
        
        # 1. Update Admission record state values to reflect closure
        discharge_query = """
            UPDATE admission 
            SET status = 'Discharged', diagnosis = %s, doctor_approved = 1, expected_discharge = CURDATE(), generated_invoice_id = %s
            WHERE admission_id = %s
        """
        db_execute(discharge_query, (final_diagnosis, invoice_id, admission_id), commit=True)
        
        # 2. BED RELEASE: Recycle the bed state flag directly back to 'Available'
        if bed_id:
            db_execute("UPDATE bed SET status = 'Available' WHERE bed_id = %s", (bed_id,), commit=True)
            
        # 3. NOTIFICATION: Dispatch automated system check alert parameters directly to the care team dashboard logs
        notif_msg = f"Patient ID {patient_id} has been safely discharged. Bed ID {bed_id} is now recycled back to active inventory configurations."
        db_execute("INSERT INTO app_notification (recipient_user_id, message) VALUES (%s, %s)", (doctor_id, notif_msg), commit=True)
        
        return {"status": "Success", "message": "Discharge transaction paths completed successfully."}
