from backend.database import db_execute

class BillingAgent:
    def generate_final_bill(self, patient_id, appointment_id, base_care_cost):
        """Compiles the absolute line-item balance sheet values into the invoice ledger table."""
        insert_invoice = """
            INSERT INTO invoice (patient_id, appointment_id, total_amount, insurance_claim, payment_status)
            VALUES (%s, %s, %s, 'None', 'Unpaid')
        """
        invoice_id = db_execute(insert_invoice, (patient_id, appointment_id, base_care_cost), commit=True)
        
        return {
            "status": "Success",
            "invoice_id": invoice_id,
            "total_amount": float(base_care_cost),
            "payment_status": "Unpaid"
        }
