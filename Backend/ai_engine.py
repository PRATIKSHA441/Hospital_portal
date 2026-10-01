import os
import datetime
from groq import Groq
from backend.db_config import execute_query

if os.getenv("GROQ_API_KEY"):
    ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
else:
    ai_client = None

def run_ai_triage_and_book(patient_id, patient_name, symptoms, target_date):
    if not ai_client:
        return {"status": "Error", "message": "Groq AI Client is uninitialized."}
        
    # 1. Ask Groq to determine specialization
    prompt = f"Analyze these patient symptoms: '{symptoms}'. Out of these values ('Cardiology', 'Emergency', 'Pediatrics', 'Maternity', 'General Medicine'), select the best matching specialization. Return ONLY the string of that specialization."
    chat_completion = ai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    detected_specialization = chat_completion.choices.message.content.strip()
    
    # 2. Match doctors
    day_name = target_date.strftime("%A")
    doc_query = """
        SELECT d.doctor_id, d.full_name, ds.start_time 
        FROM doctor d 
        JOIN doctor_schedule ds ON d.doctor_id = ds.doctor_id 
        WHERE d.specialisation = %s AND ds.day_of_week = %s AND ds.is_available = 1 
        LIMIT 1
    """
    available_doc = execute_query(doc_query, (detected_specialization, day_name), fetch=True)
    
    if not available_doc:
        available_doc = execute_query(doc_query, ("General Medicine", day_name), fetch=True)
        
    if not available_doc:
        return {"status": "Error", "message": f"No doctors found for {detected_specialization} on {day_name}."}
        
    doc = available_doc[0]
    
    # 3. Create appointment
    apt_query = """
        INSERT INTO appointment (patient_id, doctor_id, appointment_date, appointment_time, symptoms, ai_specialisation, ai_allocated_slot_time, assigned_by_ai, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 'Scheduled')
    """
    execute_query(apt_query, (patient_id, doc['doctor_id'], target_date, doc['start_time'], symptoms, detected_specialization, doc['start_time']))
    
    # Send Notification
    notif_msg = f"AI Auto-Assigned Patient {patient_name} to you for {target_date}."
    execute_query("INSERT INTO app_notification (recipient_user_id, message) VALUES (%s, %s)", (doc['doctor_id'], notif_msg))
    
    return {"status": "Success", "specialization": detected_specialization, "doctor": doc['full_name'], "time": str(doc['start_time'])}
