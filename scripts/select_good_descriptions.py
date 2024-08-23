import json
import os
import shutil
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src import ArcJsonEncoder

INPUT_DIR = 'output/all_descriptions/'
OUTPUT_DIR = 'output/good_descriptions/'

def calculate_success_rate(build_stats):
    if build_stats == "0/0":
        return 0
    successful, total = map(int, build_stats.split('/'))
    return float(successful) / total if total > 0 else 0.0

def copy_good_descriptions():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for problem_dir in os.listdir(INPUT_DIR):
        problem_path = os.path.join(INPUT_DIR, problem_dir)
        
        if not os.path.isdir(problem_path):
            continue

        description_file = os.path.join(problem_path, 'description.json')
        
        if not os.path.exists(description_file):
            continue

        with open(description_file, 'r') as f:
            description = json.load(f)

        good_descriptions = []
        for desc in description['descriptions']:
            success_rate = calculate_success_rate(desc['build_stats'])
            if success_rate > 0:
                good_descriptions.append(desc)

        if good_descriptions:
            new_problem_dir = os.path.join(OUTPUT_DIR, problem_dir)
            os.makedirs(new_problem_dir, exist_ok=True)

            # Write only good descriptions to a new JSON file
            new_description = {
                'problem_name': description['problem_name'],
                'descriptions': good_descriptions,
                'json': json.loads(description['raw_json'])
            }

            with open(os.path.join(new_problem_dir, 'good_description.json'), 'w') as f:
                #custom encoder only works with json.dumps for some reason
                formatted_json = json.dumps(new_description, cls=ArcJsonEncoder)
                f.write(formatted_json)

            # Copy all PNG files (visualizations)
            for file in os.listdir(problem_path):
                if file.endswith('.png'):
                    shutil.copy2(os.path.join(problem_path, file), new_problem_dir)

            print(f"Copied {problem_dir} to good_descriptions with {len(good_descriptions)} good subdescriptions")

if __name__ == "__main__":
    copy_good_descriptions()