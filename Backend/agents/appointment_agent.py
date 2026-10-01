from backend.database import db_execute
import datetime

class AppointmentAgent:
    def auto_assign_slot(self, patient_id, specialty, appointment_date):
        """Finds an available doctor for the given specialty and books the first open slot."""
        day_name = appointment_date.strftime("%A")
        
        # Look for active doctor match schedules
        query = """
            SELECT d.doctor_id, ds.start_time 
            FROM doctor d
            JOIN doctor_schedule ds ON d.doctor_id = ds.doctor_id
            WHERE d.specialisation = %s AND ds.day_of_week = %s AND ds.is_available = 1 AND d.is_active = 1
            LIMIT 1
        """
        doc_record = db_execute(query, (specialty, day_name), fetch=True)
        
        if not doc_record:
            # Secondary fallback check: Routing to General Medicine
            doc_record = db_execute(query, ("General Medicine", day_name), fetch=True)
            if not doc_record:
                return {"status": "Failed", "message": "No doctors scheduled for this day."}
        
        doctor_id = doc_record[0]['doctor_id']
        slot_time = doc_record[0]['start_time']
        
        # Save structural appointment logging parameters to database
        insert_sql = """
            INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, ai_specialisation, ai_allocated_slot_time, assigned_by_ai, status)
            VALUES (%s, %s, %s, %s, %s, %s, 1, 'Scheduled')
        """
        apt_id = db_execute(insert_sql, (patient_id, doctor_id, appointment_date, slot_time, specialty, slot_time))
        
        return {
            "status": "Success",
            "appointment_id": apt_id,
            "doctor_id": doctor_id,
            "allocated_time": str(slot_time)
        }
