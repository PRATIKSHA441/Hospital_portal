import http.server
import socketserver
import os
from backend.routes.appointment import handle_appointment_booking
from backend.routes.admission import handle_bed_allocation
from backend.routes.discharge import handle_discharge_transaction

PORT = 8000
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

class HospitalPortalGateway(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route standard root indices safely onto local page structures
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            os.chdir(FRONTEND_DIR)
            return super().do_GET()
        elif self.path in ['/patient.html', '/doctor.html', '/admin.html']:
            os.chdir(FRONTEND_DIR)
            return super().do_GET()
        else:
            # Fallback handling for static components
            return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response_data = {"status": "Error", "message": "Endpoint route not found."}
        
        # Route inbound REST payloads onto custom modular controllers
        if self.path == '/api/appointment/book':
            response_data = handle_appointment_booking(post_data)
        elif self.path == '/api/admission/allocate':
            response_data = handle_bed_allocation(post_data)
        elif self.path == '/api/discharge/execute':
            response_data = handle_discharge_transaction(post_data)
            
        import json
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == "__main__":
    # Ensure system state pointers find client directories
    if not os.path.exists(FRONTEND_DIR):
        print(f"⚠️ Critical System Warning: Ensure your frontend static folder is created at: {FRONTEND_DIR}")
        
    web_server = socketserver.TCPServer(("", PORT), HospitalPortalGateway)
    print(f"🚀 [PRODUCTION] Smart HIPAA Hospital Portal listening live at: http://localhost:{PORT}")
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        web_server.server_close()
        print("\nGateway terminated safely.")
