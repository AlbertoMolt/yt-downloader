from config import downloads_path

import os

def check_file(path):
    return os.path.exists(path) and os.path.isfile(path)

def check_folder(path):
    return os.path.exists(path) and os.path.isdir(path)

def check_or_create_downloads_path():
    if not check_folder(downloads_path):
        print('Downloads path not found. Attempting to create directory...')
        os.mkdir(downloads_path)