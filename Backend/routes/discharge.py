import json

from backend.agents.billing_agent import BillingAgent
from backend.agents.discharge_agent import DischargeAgent


billing_agent = BillingAgent()
discharge_agent = DischargeAgent()


def handle_discharge_transaction(request_body):
    """
    Processes billing and discharge workflow.
    """

    try:
        data = json.loads(request_body)

        admission_id = data.get("admission_id")
        patient_id = data.get("patient_id")
        appointment_id = data.get("appointment_id")
        diagnosis = data.get("diagnosis")
        base_cost = data.get("cost")

        # Generate invoice
        bill = billing_agent.generate_final_bill(
            patient_id,
            appointment_id,
            base_cost
        )

        invoice_id = bill["invoice_id"]

        # Process discharge
        result = discharge_agent.process_discharge(
            admission_id,
            diagnosis,
            invoice_id
        )

        if result["status"] == "Success":
            return {
                "status": "Success",
                "invoice_id": invoice_id,
                "message": "Discharge transaction completed successfully."
            }

        return {
            "status": "Failed",
            "message": result.get("message", "Discharge failed.")
        }

    except Exception as e:
        return {
            "status": "Error",
            "message": str(e)
        }