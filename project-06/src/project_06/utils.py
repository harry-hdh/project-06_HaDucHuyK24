import os
from pathlib import Path


def check_and_create_dir(file_path):
    parent_dir = os.path.dirname(file_path)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)

#Cleanup local file
def cleanup_local_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)