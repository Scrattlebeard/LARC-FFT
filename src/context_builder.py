import base64
from openai import OpenAI

class OpenAiContext:

    def __init__(self):
        self.messages = []
    
    def get_context(self):
        return self.messages

    def add_system_message(self, message):
        self.messages.append({"role": "system", "content": message})
    
    def add_user_message(self, message, image=None):
        if image:
            self.messages.append({"role": "user", "content": [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(image)}", "detail": "low"}} #low gives 512x512 image only, high let's the model zoom afterwards
            ]})
        else:
            self.messages.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message):
        self.messages.append({"role": "assistant", "content": message})
    
    def add_problem(self, path, problem):
        with open(f"{path}/test_input.svg", "r") as f:
            svg_input = f.read()

        msg = f"""Here is the puzzle you need to solve. Remember your training and your instructions. You can do this. Think carefully through everything step by step and solve this puzzle.
        **Puzzle Input:**
        ```json
        {problem["input"]}
        ```

        ```svg
        {svg_input}
        ```"""
        self.add_user_message(msg, image=f"{path}/test_input.png")

    def add_example(self, path, example, i):       
        input_msg = f"""**Example {i+1} Input:**        
        ```json
        {example["input"]}
        ```"""
        self.add_user_message(input_msg, image=f"{path}/train{i}_input.png")

        output_msg = f"""**Example {i+1} Output:**        
        ```json
        {example["output"]}
        ```"""
        self.add_user_message(output_msg, image=f"{path}/train{i}_output.png")

    def add_example_with_svg(self, path, example, i):
        with open(f"{path}/train{i}_input.svg", "r") as f:
            svg_input = f.read()
        
        with open(f"{path}/train{i}_output.svg", "r") as f:
            svg_output = f.read()
        
        input_msg = f"""**Example {i+1} Input:**        
        ```json
        {example["input"]}
        ```

        ```svg
        {svg_input}
        ```"""
        self.add_user_message(input_msg, image=f"{path}/train{i}_input.png")

        output_msg = f"""**Example {i+1} Output:**        
        ```json
        {example["output"]}
        ```

        ```svg
        {svg_output}
        ```"""
        self.add_user_message(output_msg, image=f"{path}/train{i}_output.png")

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    b64 = base64.b64encode(image_file.read())
    return b64.decode('utf-8')