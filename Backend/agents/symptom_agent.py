from groq import Groq
from backend.config import Config


class SymptomAgent:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)

    def analyze_symptoms(self, symptoms_text):
        """Maps symptoms to one configured medical specialty for appointment routing."""

        prompt = f"""
Analyze these clinical symptoms: '{symptoms_text}'.

Map them to exactly ONE of the following specialties:
['Cardiology', 'Pediatrics', 'Maternity', 'Emergency', 'General Medicine'].

Return ONLY the raw name of the specialty.
Do not include introductory text, explanation, or punctuation.
"""

        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama3-8b-8192",
            )

            specialty = completion.choices[0].message.content.strip()

            allowed_specialties = {
                "Cardiology",
                "Pediatrics",
                "Maternity",
                "Emergency",
                "General Medicine"
            }

            if specialty in allowed_specialties:
                return specialty

            return "General Medicine"

        except Exception:
            return "General Medicine"