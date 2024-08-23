import os
import random
import shutil

if __name__ == "__main__":
    folder = "output/gpt4_solved"
    set_size = 10    

    # Get all subdirectories
    all_subdirs = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]  
    selected_subdirs = random.sample(all_subdirs, min(set_size, len(all_subdirs)))

    os.makedirs(f"testsets/gpt4_solved-all", exist_ok=False)
    for name in all_subdirs:
        src_path = os.path.join(folder, name)
        dst_path = os.path.join(f"testsets/gpt4_solved-all", name)
        shutil.copytree(src_path, dst_path)