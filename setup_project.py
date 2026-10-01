import os

# Define the production enterprise layout
structure = [
    "database/schema.sql",
    "database/seed_data.sql",
    "backend/__init__.py",
    "backend/db_config.py",
    "backend/ai_engine.py",
    "frontend/__init__.py",
    "frontend/app.py",
    ".gitignore",
    ".env",
    "requirements.txt",
    "README.md"
]

for file_path in structure:
    # Create directory if it doesn't exist
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    # Create empty file if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            if "gitignore" in file_path:
                f.write(".env\n__pycache__/\n*.pyc\n.streamlit/\n")
            elif "requirements" in file_path:
                f.write("streamlit==1.32.0\nmysql-connector-python==8.3.0\ngroq==0.5.0\npython-dotenv==1.0.1\n")
        print(f"Created: {file_path}")

print("\n🚀 Project structure built successfully! Delete this setup script now.")
