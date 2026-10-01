import json
from backend.agents.bed_agent import BedAgent
from backend.database import db_execute

bed_agent = BedAgent()

def handle_bed_allocation(request_body):
    """
    Checks real-time bed inventory states and issues an official lock.
    """
    try:
        data = json.loads(request_body)
        patient_id = data.get("patient_id")
        doctor_id = data.get("doctor_id")
        bed_type = data.get("bed_type")
        reason = data.get("reason")
        
        # Step 1: Use atomic agent to allocate an available bed space
        allocation = bed_agent.check_allocated_bed(bed_type)
        if allocation["status"] == "Failed":
            return {"status": "Failed", "message": allocation["message"]}
            
        bed_id = allocation["bed_id"]
        bed_number = allocation["bed_number"]
        
        # Step 2: Register active admission mapping
        insert_query = """
            INSERT INTO admission (patient_id, doctor_id, bed_id, admission_reason, status)
            VALUES (%s, %s, %s, %s, 'Admitted')
        """
        db_execute(insert_query, (patient_id, doctor_id, bed_id, reason), commit=True)
        
        return {
            "status": "Success",
            "bed_id": bed_id,
            "bed_number": bed_number
        }
    except Exception as e:
        return {"status": "Error", "message": str(e)}
