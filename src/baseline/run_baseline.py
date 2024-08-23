import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src import context_builder
from src import experiment_runner

initial_prompt = """You are an advanced AI highly skilled in logic, pattern recognition and visual and spatial reasoning.
You are very detail-oriented, observant and you work meticulously when solving problems.

The ARC benchmark is a collection of problems that are designed to test the ability of AI systems to reason about abstract concepts and solve complex problems.
We will be working to prove that advanced AIs like you can easily solve such puzzles by utilizing stringent logic and unfaltering attention to details.
There is a total prize sum of $1,000,000 (one million dollars) at stake.

You will be given problem representations as json, svg and as a picture.
First, you will be given examples of input patterns and their corresponding outputs.
Then, you will be given one or more descriptions of the transformation rule that governs how the input pattern is transformed into the output pattern.

Finally, you will be given a problem, and your job is to solve it correctly.
"""

def build_context(problem, testset):
    problem_path = f"testsets/{testset}/{problem['task_name']}".replace(".json", "")

    context = context_builder.OpenAiContext()
    context.add_system_message(initial_prompt)
    
    context.add_user_message("Here are the examples:")

    for i, example in enumerate(problem["training_grids"]):
        context.add_example(problem_path, example, i)
    
    context.add_user_message("Next, you will see some descriptions that others have used to solve this puzzle:")

    for i, description in enumerate(description for description in problem["descriptions"] if is_good_description(description)):
            context.add_user_message(create_description_message(description, i))
    
    context.add_problem(problem_path, problem["test_grid"][0])

    return problem["task_name"], context

def is_good_description(description, success_threshold=0.0):
    if not description["is_verified"] or len(description["builds"]) == 0:
        return False
    
    successful_builds = sum(1 for build in description["builds"] if build["is_success"])
    success_rate = successful_builds / len(description["builds"])
    
    return success_rate > success_threshold

def create_description_message(description, i):
    return f""" **Description {i+1}:**
    {description["description_input"].replace("...", " ")}
    {description["description_output_grid_size"].replace("...", " ")}
    {description["description_output_instructions"].replace("...", " ")}
    """

if __name__ == "__main__":
    testset = "gpt4_solved-all"
    model = "gpt-4o-mini"
    path = "experiments/baseline-5"
    testset_path = f"testsets/{testset}"

    contexts = []

    for problem_folder in os.listdir(testset_path):
        problem_path = os.path.join(testset_path, problem_folder)
        if os.path.isdir(problem_path):
            json_file = os.path.join(problem_path, f"{problem_folder}.json")
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    problem = json.load(f)
                
                task_name, context = build_context(problem, testset)
                contexts.append((task_name, context))
    
    experiment_runner.create_batch_file(path, "baseline", contexts, model)
    experiment_runner.run_batch(path, "baseline")