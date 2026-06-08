import os 
from pathlib import Path
import logging 

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s]: %(message)s")


list_of_files = [
    "models/__init__.py",
    
    
    "data/.gitkeep",
    "data/documents/tip_device_best_practices.txt",
    "data/documents/tip_energy_savings.txt",

    "agent.py",
    "tools.py",
    
    "01_db_setup.ipynb",
    "02_rag_setup.ipynb",
    "03_run_and_evaluate.ipynb",

    "README.md",
    ".gitignore",

    "requirements.txt",
    ".env",
    ".env.example",]


for file_path in list_of_files:
    file_path =  Path(file_path)
    file_dir,file_name = os.path.split(file_path)

    if file_dir != "":
        os.makedirs(file_dir,exist_ok=True)
        logging.info(f"Creating directory: {file_dir} for file: {file_name}")

    if (not os.path.exists(file_path)) or (os.path.getsize(file_path) == 0):
        with open(file_path,"w") as f:
            pass
            logging.info(f"Creating an empty file: {file_path}")
    
    else:
        logging.info(f"{file_name} already exists")