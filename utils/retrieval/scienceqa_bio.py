# scienceqa_bio
from typing import Optional, Any
import transformers
import torch
from peft import PeftModel
from transformers.utils import is_accelerate_available, is_bitsandbytes_available
from transformers import (
    AutoModel,
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    pipeline,
)
import re
import utils.globalvar
import datasets

# prompt = """
# ### Instruction: Answer the question truthfully.
# ### Input: What are some possible causes of low PTH and high calcium levels?
# ### Output: 
# """

def formatting_prompts_func(ipt):
    text = f"### Instruction: Answer the question truthfully.\n### Input: {ipt}\n### Output: "
    return text


### Query Generation ###############################################
def llama2_pipeline(prompt):
    base_model = "meta-llama/Llama-2-7b-hf"
    peft_model = "veggiebird/llama-2-7b-biology-scienceqa-8bit"
    
    # load the model only once
    if utils.globalvar.bio_model is None:
        utils.globalvar.bio_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            use_safetensors=True,
            torch_dtype=torch.float16,
            load_in_8bit=True
        )

        utils.globalvar.bio_model = PeftModel.from_pretrained(utils.globalvar.bio_model, peft_model)

        utils.globalvar.bio_tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    print("Model loaded...")
    pipeline = transformers.pipeline(
        "text-generation",
        model=utils.globalvar.bio_model,
        tokenizer=utils.globalvar.bio_tokenizer,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    sequences = pipeline(
        prompt,
        do_sample=False,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=utils.globalvar.bio_tokenizer.eos_token_id,
        max_length=256,
    )
    
    return sequences[0]["generated_text"].strip()

def gpt_pipeline(prompt):
    import requests
    HTTP_LLM_API_KEY='eyJ0eXAiOiJqd3QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjM5NDc3MyIsInBhc3N3b3JkIjoiMzk0NzczMTIzIiwiZXhwIjoyMDIxNjE4MzE3fQ.oQx2Rh-GJ_C29AfHTHE4x_2kVyy7NamwQRKRA4GPA94'
    OPENAI_API_KEY='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'
    # print(f"prompt:{prompt}")

    url = "http://47.88.8.18:8088/api/ask"
    headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + HTTP_LLM_API_KEY
            }
    data = {
            "model": 'gpt-4',
            "messages": [{"role": "user", "content": prompt}],
            "n": 1,
            "temperature": 0.0
            }
    response = requests.post(url, json=data, headers=headers)
    response = response.json()
    new_response = response['data']['response']

    return new_response["choices"][0]["message"]["content"].strip()

###############################################

### Query Knowl. ###############################################
def extract_responses(content):
    pattern = r"### Output:(.+?)###"
    matches = re.findall(pattern, content, re.DOTALL)
    return [match.strip() for match in matches]


def generate_scienceqa_bio_query(input):
    prompt = formatting_prompts_func(input)
    # query = llama2_pipeline(prompt)
    query = gpt_pipeline(prompt)
    processed_query = extract_responses(query)
    return query, processed_query


def execute_scienceqa_bio_query(query):
    model = AutoModel.from_pretrained("princeton-nlp/sup-simcse-roberta-large")
    tokenizer = AutoTokenizer.from_pretrained("princeton-nlp/sup-simcse-roberta-large")
    dataset = datasets.load_dataset('veggiebird/biology-scienceqa')
    dataset = dataset["train"]
    dataset.add_faiss_index(column='embeddings')
    
    query_inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    query_embedding = model(**query_inputs, output_hidden_states=True, return_dict=True).pooler_output.detach().numpy()
    scores, retrieved_Examples = dataset.get_nearest_examples("embeddings", query_embedding, k=1)
    pre_knowl = retrieved_Examples["output"][0].strip()
    try:
        knowl = ' '.join(re.split(r'(?<=[.:;])\s', pre_knowl)[:3])
    except:
        knowl = pre_knowl
    return knowl

###############################################

def retrieve_scienceqa_bio_knowledge(input, data_point):
    knowl = ""
    print("Generate query...")
    query, processed_query = generate_scienceqa_bio_query(input)
    if len(processed_query) != 0:
        print("Query:", processed_query[0])
        print("Retrieve knowledge...")
        knowl = execute_scienceqa_bio_query(processed_query[0])
    print(knowl)
    return knowl