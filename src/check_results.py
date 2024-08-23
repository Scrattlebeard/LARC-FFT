import json

def remove_newlines_and_spaces(text):
    return text.replace("\n", "").replace(" ", "")

if __name__ == "__main__":
    path = "experiments/baseline-5"
    with open(f"{path}/baseline_output.jsonl", "r") as f:
        results = f.readlines()

        success = []
        total = len(results)
        for result in results:
            result = json.loads(result)
            answer = remove_newlines_and_spaces(result["response"]["body"]["choices"][0]["message"]["content"])

            problem_file = result["custom_id"]
            with open(f"testsets/gpt4_solved-all/{problem_file.replace('.json', '')}/{problem_file}", "r") as f:
                problem = json.load(f)
                correct_json = remove_newlines_and_spaces(f"{problem["test_grid"][0]["output"]}")

                if f"{correct_json}" in answer:
                    success.append(problem_file)
                else:
                    with open(f"testsets/gpt4_solved-all/{problem_file.replace('.json', '')}/test_output.svg", "r") as f:
                        correct_svg = remove_newlines_and_spaces(f.read())
                        if correct_svg in answer:
                            success.append(problem_file)

        print(f"Success: {len(success)}, Total: {total}, Accuracy: {len(success)/total}")
        for problem in success:
            print(f"Solved {problem}")