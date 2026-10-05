# Hospital_portal
A web-based Hospital Portal for managing patients, doctors, appointments, medical records, and billing through a secure and user-friendly system.
# 🏥 AI-Driven HIPAA Hospital Management Portal

An advanced, role-based hospital management engine powered by **Python, MySQL, and Groq AI (Llama 3)**.

## 🚀 Core Automations Built-in
* **Smart Triage (Patient Panel):** Evaluates input patient symptoms using Groq AI, identifies clinical specialization needs, reads active doctor schedules from MySQL, and auto-books open slots.
* **Bed Inventory Manager (Receptionist Panel):** Features atomic database status-locking to automatically check, assign, and recycle beds safely without manual entries.
* **One-Click Discharge Engine (Doctor Panel):** Automatically generates line-item billing invoices upon discharge and immediately flags hospital beds back to an `Available` status.

## 📁 System Architecture Layout
* `/database`: Houses core data schemas designed directly for MySQL Workbench.
* `/backend`: Manages transaction handling, secure SQL isolation, and Groq LLM processing calls.
* `/frontend`: Implements the multi-dashboard view utilizing Streamlit.

## ⚡ Local Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure database access details inside a local `.env` file.
3. Start the interface: `streamlit run frontend/app.py`
