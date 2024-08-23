import json
import os
from openai import OpenAI

def create_batch_file(folder, batch_name, contexts, model="gpt-4o-mini", generations=1):
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/{batch_name}.jsonl", "w") as file:
        for (task_name, context) in contexts:
            req = {"custom_id": f"{task_name}", "method": "POST", "url": "/v1/chat/completions", "body": {"model": model, "messages": context.messages, "n": generations}}
            file.write(json.dumps(req)+ "\n")

def run_batch(folder, batch_name):    
    client = OpenAI()

    batch_input_file = client.files.create(
        file=open(f"{folder}/{batch_name}.jsonl", "rb"),
        purpose="batch"
    )

    batch_input_file_id = batch_input_file.id

    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": batch_name
        }
    )

    print(f"Batch {batch_name} created with id {batch.id}")
    with open(f"{folder}/{batch_name}.txt", "w") as file:
        file.write(str(batch))

def check_batch(folder, batch_name):
    with open(f"{folder}/{batch_name}.txt", "r") as file:
        batch = json.load(file)
    
    client = OpenAI()
    batch = client.batches.retrieve(batch.id)
    
    with open(f"{folder}/{batch_name}.txt", "w") as file:
        file.write(str(batch))
    
    print(f"Batch {batch_name} with id {batch.id} has status {batch.status}")

    if batch.status == "completed":
        res = client.files.content(batch.output_file_id)
        with open(f"{folder}/{batch_name}_output.jsonl", "w") as file:
            file.write(res)