import os
import shutil


def create_folder_if_not_exists(folder_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
