from backend.database import db_execute

class BedAgent:
    def check_and_allocate_bed(self, required_bed_type):
        """Scans the inventory database for an 'Available' bed and changes its state status."""
        # Find an open bed of the requested category type
        find_query = """
            SELECT bed_id, bed_number FROM bed 
            WHERE bed_type = %s AND status = 'Available' 
            LIMIT 1
        """
        free_bed = db_execute(find_query, (required_bed_type,), fetch=True)
        
        if not free_bed:
            return {"status": "Failed", "message": f"No {required_bed_type} beds available."}
            
        bed_id = free_bed[0]['bed_id']
        bed_number = free_bed[0]['bed_number']
        
        # Update status to Occupied to prevent double booking
        update_query = "UPDATE bed SET status = 'Occupied' WHERE bed_id = %s"
        db_execute(update_query, (bed_id,), commit=True)
        
        return {
            "status": "Success",
            "bed_id": bed_id,
            "bed_number": bed_number
        }
