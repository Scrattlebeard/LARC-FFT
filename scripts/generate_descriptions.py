import json
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from collections import defaultdict

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src import grid_to_svg, render_svg

# Paths to the data directories
SUMMARY_DIR = 'dataset/summary/'
TRAINING_DIR = 'collection/data/training/'
OUTPUT_DIR = 'output/all_descriptions/'

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_csv(file_path):
    data = defaultdict(list)
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for header, value in row.items():
                data[header].append(value)
    return data

def generate_visualization(grid, output_path):
    # Convert grid to numpy array
    grid_array = np.array(grid)

    # Create a new figure
    fig, ax = plt.subplots()

    # Define the color map based on the .js visualizations
    color_map = {
        0: '#000000',  # black
        1: '#0074D9',  # blue
        2: '#FF4136',  # red
        3: '#2ECC40',  # green
        4: '#FFDC00',  # yellow
        5: '#AAAAAA',  # grey
        6: '#F012BE',  # fuschia
        7: '#FF851B',  # orange
        8: '#7FDBFF',  # teal
        9: '#870C25'   # brown
    }

    # Create a ListedColormap
    custom_cmap = ListedColormap([color_map[i] for i in range(10)])

    # Display the grid with the custom color map
    cax = ax.imshow(grid_array, cmap=custom_cmap, vmin=0, vmax=9)

    # Add grid lines
    ax.grid(which='major', color='w', linestyle='-', linewidth=4)

    # Set ticks to be in the middle of each cell
    ax.set_xticks(np.arange(0.5, len(grid_array[0]), 1))
    ax.set_yticks(np.arange(0.5, len(grid_array), 1))

    # Remove tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Save the figure as PNG
    plt.savefig(output_path, bbox_inches='tight')
    
    # Save the figure as SVG
    svg_output_path = output_path.rsplit('.', 1)[0] + '.svg'
    plt.savefig(svg_output_path, bbox_inches='tight', format='svg')
    
    plt.close(fig)

def generate_problem_descriptions():
    # Load summary data
    task_summary = load_csv(os.path.join(SUMMARY_DIR, 'task.csv'))
    description_summary = load_csv(os.path.join(SUMMARY_DIR, 'description.csv'))
    join_summary = load_csv(os.path.join(SUMMARY_DIR, 'join.csv'))
    build_summary = load_csv(os.path.join(SUMMARY_DIR, 'build.csv'))

    # Process each task
    for task_number in task_summary['task_id']:
        task_file = f"{task_number}.json"

        # Extract required information
        task_name = task_summary['task_name'][int(task_number)]
        descriptions = []

        # Get descriptions for this task
        task_descriptions = [desc for i, desc in enumerate(join_summary['description_id']) 
                             if join_summary['task_id'][i] == task_number]

        for desc_id in task_descriptions:
            desc_index = description_summary['description_id'].index(desc_id)
            
            # Count build attempts and successful builds for this description
            build_attempts = 0
            successful_builds = 0
            for i, build_desc_id in enumerate(join_summary['description_id']):
                if build_desc_id == desc_id:
                    build_id = join_summary['build_id'][i]
                    if build_id != '':
                        build_index = build_summary['build_id'].index(build_id)
                        build_attempts += 1
                        if build_summary['is_success'][build_index] == 'True':
                            successful_builds += 1
            
            description = {
                'input_instructions': description_summary['description_input'][desc_index].replace('...', ' '),
                'output_grid_size': description_summary['description_output_grid_size'][desc_index].replace('...', ' '),
                'output_instructions': description_summary['description_output'][desc_index].replace('...', ' '),
                'is_verified': description_summary['is_verified'][desc_index],
                'task_solved': successful_builds > 0,
                'build_stats': f"{successful_builds}/{build_attempts}"
            }
            descriptions.append(description)

        # Read the raw JSON from the training file
        task_file = f"{task_name}"
        with open(os.path.join(TRAINING_DIR, task_file), 'r') as f:            
            raw_json_string = f.read()
            raw_json = json.loads(raw_json_string)

        # Create output directory for this problem
        problem_dir = os.path.join(OUTPUT_DIR, f"problem_{task_number}")
        os.makedirs(problem_dir, exist_ok=True)

        # Generate visualizations for training examples
        for i, example in enumerate(raw_json['train']):
            input_path = os.path.join(problem_dir, f"train_{i+1}_input.png")
            output_path = os.path.join(problem_dir, f"train_{i+1}_output.png")
            with open(input_path, 'w') as f:
                f.write(grid_to_svg(example['input']))
            with open(output_path, 'w') as f:
                f.write(grid_to_svg(example['output']))

        # Generate visualizations for test examples
        for i, example in enumerate(raw_json['test']):
            input_path = os.path.join(problem_dir, f"test_{i+1}_input.svg")
            output_path = os.path.join(problem_dir, f"test_{i+1}_output.svg")
            with open(input_path, 'w') as f:
                f.write(grid_to_svg(example['input']))
                
            with open(output_path, 'w') as f:
                f.write(grid_to_svg(example['output']))

        # Format the problem description as a dictionary
        problem_description = {
            "problem_name": task_name,
            "descriptions": descriptions,
            "raw_json": raw_json_string
        }

        # Write the description to a JSON file
        output_file = os.path.join(problem_dir, "description.json")
        with open(output_file, 'w') as f:
            json.dump(problem_description, f, indent=2)

        print(f"Generated JSON description and visualizations for problem {task_number}")

if __name__ == "__main__":
    generate_problem_descriptions()