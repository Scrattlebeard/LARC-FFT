from openai import OpenAI

if __name__ == "__main__":
    client = OpenAI()
    batch = client.batches.retrieve("batch_9NuUoveuceMq8ok24Bvd0l6b")
    
    print(f"Batch with id {batch.id} has status {batch.status}")

    with open(f"experiments/baseline-5/baseline.txt", "w") as file:
        file.write(str(batch))

    print(str(batch))

    if batch.status == "completed":
        if(batch.output_file_id is not None):
            res = client.files.content(batch.output_file_id)
            res_content = res.read()
            with open(f"experiments/baseline-5/baseline_output.jsonl", "wb") as file:
                file.write(res_content)
        elif(batch.error_file_id is not None):
            res = client.files.content(batch.error_file_id)
            res_content = res.read()
            with open(f"experiments/baseline-5/baseline_error.jsonl", "wb") as file:
                file.write(res_content)
        else:
            print("No output file id found")
    