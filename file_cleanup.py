from config import downloads_path
from utils import check_or_create_downloads_path

import json
import os

files_dict = {}

def get_max_storage():
    with open('config.json', 'r') as file:
        config = json.load(file)

    return config['mb_max_storage_size']

def get_files_info():
    total_size_mb = 0
    check_or_create_downloads_path()
    
    for filename in os.listdir(downloads_path):
        file_path = os.path.join(downloads_path, filename)
        if os.path.isfile(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            total_size_mb += size_mb
            mod_time = os.path.getmtime(file_path)
            
            files_dict[filename] = {
                "path": file_path,
                "size_mb": size_mb,
                "mod_time": mod_time
            }
            
    return files_dict

def get_total_size():
    total_size_mb = 0
    check_or_create_downloads_path()
    
    for filename in os.listdir(downloads_path):
        file_path = os.path.join(downloads_path, filename)
        if os.path.isfile(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            total_size_mb += size_mb
            
    return total_size_mb

def delete_old_files():
    files_dict  = get_files_info()
    total_size_mb = get_total_size()
    
    sorted_files = sorted(
        files_dict.items(),
        key=lambda x: x[1]["mod_time"]
    )
    
    removed_files = 0
    
    for name, info in sorted_files:
        if total_size_mb <= get_max_storage():
            break
        
        removed_files += 1
        os.remove(info["path"])
        total_size_mb -= info["size_mb"]
        del files_dict[name]
        
    print(f"{removed_files} file{'s' if removed_files != 1 else ''} has been removed.")

def make_space(file_size):
    max_storage = get_max_storage()
    total_size_mb = get_total_size()
    
    new_size = total_size_mb + (file_size / (1024 * 1024))
    
    print("Storage occupied + new file:")
    print(f"    {new_size:.2f} MB / {max_storage} MB")
    
    if new_size > max_storage:
        print("⚠️ Max storage space exceeded")
        delete_old_files()
    else:
        print("✅ All good")
        
def check_space():
    max_storage = get_max_storage()
    total_size_mb = get_total_size()
    
    print("Storage occupied:")
    print(f"    {total_size_mb:.2f} MB / {max_storage} MB")
    
    if total_size_mb > max_storage:
        print("⚠️ Max storage space exceeded")
        delete_old_files()
    else:
        print("✅ All good")