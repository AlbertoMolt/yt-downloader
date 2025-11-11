import json
import os

downloads_path = 'downloads'

with open('config.json', 'r') as file:
    config = json.load(file)

mb_max_storage_size = config['mb_max_storage_size']
files_dict = {}
total_size_mb = 0

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
        
        
def delete_old_files():
    sorted_files = sorted(
        files_dict.items(),
        key=lambda x: x[1]["mod_time"]
    )
    
    total = total_size_mb
    removed_files = 0
    
    for name, info in sorted_files:
        if total <= mb_max_storage_size:
            break
        
        removed_files += 1
        os.remove(info["path"])
        total -= info["size_mb"]
        del files_dict[name]
        
    print(f"{removed_files} file(s) has been removed.")

print(f"{total_size_mb:.2f} MB / {mb_max_storage_size} MB")

if total_size_mb > mb_max_storage_size:
    print("⚠️ Max storage space exceeded")
    delete_old_files()
else:
    print("✅ All good")