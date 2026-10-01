import json
from datetime import datetime
from backend.agents.symptom_agent import SymptomAgent
from backend.agents.appointment_agent import AppointmentAgent

# Instantiate workflow components
symptom_agent = SymptomAgent()
appointment_agent = AppointmentAgent()

def handle_appointment_booking(request_body):
    """
    Endpoint controller block matching your exact diagram:
    Input Symptoms -> Run AI Symptom Agent -> Detect Specialty -> Route to Appointment Agent -> Save Allocation
    """
    try:
        data = json.loads(request_body)
        patient_id = data.get("patient_id")
        symptoms_text = data.get("symptoms")
        date_str = data.get("date", datetime.today().strftime('%Y-%m-%d'))
        
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Step 1 & 2: Process text properties via Groq AI
        detected_specialty = symptom_agent.analyze_symptoms(symptoms_text)
        
        # Step 3 & 4: Search calendar constraints and register allocation
        booking_result = appointment_agent.auto_assign_slot(patient_id, detected_specialty, parsed_date)
        
        if booking_result["status"] == "Success":
            return {
                "status": "Success",
                "specialization": detected_specialty,
                "doctor_id": booking_result["doctor_id"],
                "allocated_time": booking_result["allocated_time"]
            }
        else:
            return {"status": "Failed", "message": booking_result["message"]}
            
    except Exception as e:
        return {"status": "Error", "message": str(e)}
