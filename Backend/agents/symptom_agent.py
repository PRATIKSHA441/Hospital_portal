from groq import Groq
from backend.config import Config

class SymptomAgent:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)

    def analyze_symptoms(self, symptoms_text):
        """Analyzes symptoms to map them to an explicit medical specialty."""
        prompt = f"""
        Analyze these clinical symptoms: '{symptoms_text}'.
        Map them to exactly ONE of the following specialties:
        ['Cardiology', 'Pediatrics', 'Maternity', 'Emergency', 'General Medicine'].
        Return ONLY the raw name of the specialty. Do not include introductory text or punctuation.
        """
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return completion.choices.message.content.strip()
        except Exception:
            return "General Medicine"  # Fallback safety standard
