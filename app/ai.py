import openai
import torch
from transformers import AutoTokenizer

# NOTE: from https://blog.devgenius.io/how-to-get-around-openai-gpt-3-token-limits-b11583691b32


openai.api_key = ...

def count_tokens(filename):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    with open(filename, 'r') as f:
        text = f.read()

    input_ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0)
    num_tokens = input_ids.shape[1]
    return num_tokens

def break_up_file_to_chunks(filename, chunk_size=1500, overlap=100):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    with open(filename, 'r') as f:
        text = f.read()

    tokens = tokenizer.encode(text)
    num_tokens = len(tokens)
    
    chunks = []
    for i in range(0, num_tokens, chunk_size - overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

prompt_response = []

tokenizer = AutoTokenizer.from_pretrained("gpt2")

chunks = break_up_file_to_chunks('./app/doc.txt')

for i, chunk in enumerate(chunks):
    prompt_request = "Sumarizuj tuto část článku: " + tokenizer.decode(chunks[i])
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_request,
        temperature=0.5,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0
    )
    prompt_response.append(response["choices"][0]["text"].strip())
    # print(response["choices"][0]["text"].strip())


prompt_request = "Udělej sumarizaci následujících informací: " + str(prompt_response)
response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_request,
        temperature=.5,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
meeting_summary = response["choices"][0]["text"].strip()

print(meeting_summary)
