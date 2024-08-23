import arc_utils
import csv
import json
import os
from arc_json_formatter import ArcJsonEncoder

class LarcTask:
    def __init__(self, task_number, task_name, test_input_size, test_output_size, example_input_sizes, example_output_sizes, number_of_examples):
        self.task_number = task_number
        self.task_name = task_name
        self.test_input_size = test_input_size
        self.test_output_size = test_output_size
        self.example_input_sizes = example_input_sizes
        self.example_output_sizes = example_output_sizes
        self.number_of_examples = number_of_examples

class LarcDescription:
    def __init__(self, description_id, user_id, description_input, description_output_grid_size, description_output_instructions, is_verified, confidence, num_verification_attempts, num_actions, generation, user_num_prior_description_experiences, user_num_prior_build_experiences, description_synthesis_time, verification_time):
        self.description_id = description_id
        self.user_id = user_id
        self.description_input = description_input
        self.description_output_grid_size = description_output_grid_size
        self.description_output_instructions = description_output_instructions
        self.is_verified = is_verified
        self.confidence = confidence
        self.num_verification_attempts = num_verification_attempts
        self.num_actions = num_actions
        self.generation = generation
        self.user_num_prior_description_experiences = user_num_prior_description_experiences
        self.user_num_prior_build_experiences = user_num_prior_build_experiences
        self.description_synthesis_time = description_synthesis_time
        self.verification_time = verification_time

class LarcBuild:
    def __init__(self, build_id, user_id, is_success, num_attempts, num_actions, user_num_prior_description_experiences, user_num_prior_build_experiences, build_time):
        self.build_id = build_id
        self.user_id = user_id
        self.is_success = is_success
        self.num_attempts = num_attempts
        self.num_actions = num_actions
        self.user_num_prior_description_experiences = user_num_prior_description_experiences
        self.user_num_prior_build_experiences = user_num_prior_build_experiences
        self.build_time = build_time

class LarcJoin:
    def __init__(self, task_number, description_id, build_id):
        self.task_number = task_number
        self.description_id = description_id
        self.build_id = build_id

class Problem:
    def __init__(self, task_name, task_number, descriptions, training_grids, test_grid):
        self.task_name = task_name
        self.task_number = int(task_number)
        self.descriptions = descriptions
        self.training_grids = training_grids
        self.test_grid = test_grid

    def to_dict(self):
        return {
            'task_name': self.task_name,
            'task_number': self.task_number,
            'descriptions': [desc.to_dict() for desc in self.descriptions],
            'training_grids': self.training_grids,
            'test_grid': self.test_grid
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['task_name'],
            data['task_number'],
            [Description.from_dict(desc) for desc in data['descriptions']],
            data['training_grids'],
            data['test_grid']
        )

class Description:
    def __init__(self, description_id, task_name, description_input, description_output_grid_size, description_output_instructions, is_verified, confidence, num_verification_attempts, builds):
        self.description_id = description_id
        self.task_name = task_name
        self.description_input = description_input
        self.description_output_grid_size = description_output_grid_size
        self.description_output_instructions = description_output_instructions
        self.is_verified = is_verified == "True"
        self.confidence = int(confidence) if confidence != "" else None
        self.num_verification_attempts = int(num_verification_attempts)
        self.builds = builds
    
    def to_dict(self):
        return {
            'description_id': self.description_id,
            'task_name': self.task_name,
            'description_input': self.description_input,
            'description_output_grid_size': self.description_output_grid_size,
            'description_output_instructions': self.description_output_instructions,
            'is_verified': self.is_verified,
            'confidence': self.confidence,
            'num_verification_attempts': self.num_verification_attempts,
            'builds': [build.to_dict() for build in self.builds]
        }

class Build:
    def __init__(self, build_id, description_id, is_success, num_attempts):
        self.build_id = build_id
        self.description_id = description_id
        self.is_success = is_success == "True"
        self.num_attempts = int(num_attempts)

    def to_dict(self):
        return {
            'build_id': self.build_id,
            'description_id': self.description_id,
            'is_success': self.is_success,
            'num_attempts': self.num_attempts
        }

def read_larc_data(dataset_folder = "dataset/summary/", problem_folder = "collection/data/training/"):

    larc_tasks = read_tasks(dataset_folder + "task.csv")
    larc_descriptions = read_descriptions(dataset_folder + "description.csv")
    larc_builds = read_builds(dataset_folder + "build.csv")
    larc_joins = read_joins(dataset_folder + "join.csv")

    builds = []
    for larc_build in larc_builds:
        description_id = next((x.description_id for x in larc_joins if x.build_id == larc_build.build_id), None)
        builds.append(Build(larc_build.build_id, description_id, larc_build.is_success, larc_build.num_attempts))
    
    descriptions = []
    for larc_description in larc_descriptions:
        task_name = larc_tasks[int(next((x.task_number for x in larc_joins if x.description_id == larc_description.description_id), None))].task_name
        desc_builds = [build for build in builds if build.description_id == larc_description.description_id]
        descriptions.append(Description(larc_description.description_id, task_name, larc_description.description_input, larc_description.description_output_grid_size, larc_description.description_output_instructions, larc_description.is_verified, larc_description.confidence, larc_description.num_verification_attempts, desc_builds))
    
    problems = []
    for task in larc_tasks:
        task_descriptions = [description for description in descriptions if description.task_name == task.task_name]
        (training_grids, test_grid) = read_training_and_test_grids(problem_folder + task.task_name)
        problems.append(Problem(task.task_name, task.task_number, task_descriptions, training_grids, test_grid))

    return problems

def read_tasks(filename):    
    larc_tasks = []
    with open(filename, "r") as file:
        reader = csv.reader(file)   
        next(reader)  # Skip the header line
        for row in reader:
            larc_tasks.append(LarcTask(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
    return larc_tasks

def read_descriptions(filename):
    larc_descriptions = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            larc_descriptions.append(LarcDescription(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
    return larc_descriptions

def read_builds(filename):
    larc_builds = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            larc_builds.append(LarcBuild(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    return larc_builds

def read_joins(filename):
    larc_joins = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            larc_joins.append(LarcJoin(row[0], row[1], row[2]))
    return larc_joins

def read_training_and_test_grids(filename):
    with open(filename, "r") as file:
        data = json.load(file)
        return data["train"], data["test"]

def read_gpt4_tasks(filename):
    with open(filename, "r") as file:
        data = json.load(file)
        return data

def was_solved_by_gpt4(gpt4problem):
    target = json.dumps(gpt4problem["problem"]["test"][0]["output"])
    solutions = [gpt4problem["gpt4"].get("nl_only", ""), gpt4problem["gpt4"].get("nl_and_io", ""), gpt4problem["gpt4"].get("io_only", ""), gpt4problem["gpt4"].get("nothing", ""), gpt4problem["gpt4"].get("io_to_inst", "")]
    return any(grab_output(solution) == target for solution in solutions)

#from authors repo
def grab_output(gpt4_response):
    try:
        # parse the content between [[ and ]] for the grid, inclusive, 
        # there might be multiple grids, but we only care about the LAST one
        gpt4_response_grid = gpt4_response.split("[[")[-1]
        gpt4_response_grid = gpt4_response_grid.split("]]")[0]
        gpt4_response_grid = "[[" + gpt4_response_grid + "]]"
        return gpt4_response_grid
    except:
        return None

if __name__ == "__main__":
    
    problems = read_larc_data()
    print(f"Read {len(problems)} problems, expected 400...")

    solved_problems = [problem for problem in problems if any(any(build.is_success for build in description.builds) for description in problem.descriptions)]
    print(f"Read {len(solved_problems)} solved problems, expected 354...")

    gpt4tasks = read_gpt4_tasks("gpt4_successful_tasks_with_descriptor.json")
    names = list(set(task["name"] for task in gpt4tasks))
    print(f"Read {len(names)} gpt4 tasks, expected 354...")

    gpt4_solved_problems = [problem for problem in solved_problems if was_solved_by_gpt4(next((x for x in gpt4tasks if x["name"] == problem.task_name), None))]
    print(f"Read {len(gpt4_solved_problems)} gpt4 solved problems, that leaves {364 - len(gpt4_solved_problems)} unsolved, expected 245 unsolved...")

    for problem in gpt4_solved_problems:

        name = problem.task_name.replace('.json', '')
        os.makedirs(f"output/gpt4_solved/{name}", exist_ok=True)

        with open(f"output/gpt4_solved/{name}/{name}.json", "w") as file:
            json.dump(problem.to_dict(), file, indent=4, cls=ArcJsonEncoder)

        for i, task in enumerate(problem.training_grids):
            input_svg = arc_utils.grid_to_svg(task["input"])
            file_name = f"output/gpt4_solved/{name}/train{i}_input.svg"
            with open(file_name, "w") as file:
                file.write(input_svg)
                file.flush()
            arc_utils.render_svg(file_name)
            
            output_svg = arc_utils.grid_to_svg(task["output"])
            file_name = f"output/gpt4_solved/{name}/train{i}_output.svg"
            with open(file_name, "w") as file:
                file.write(output_svg)
                file.flush()
            arc_utils.render_svg(file_name)
        
        for task in problem.test_grid:            
            input_svg = arc_utils.grid_to_svg(task["input"])
            file_name = f"output/gpt4_solved/{name}/test_input.svg"
            with open(file_name, "w") as file:
                file.write(input_svg)
                file.flush()
            arc_utils.render_svg(file_name)
            
            output_svg = arc_utils.grid_to_svg(task["output"])
            file_name = f"output/gpt4_solved/{name}/test_output.svg"
            with open(file_name, "w") as file:
                file.write(output_svg)
                file.flush()
            arc_utils.render_svg(file_name)
        



