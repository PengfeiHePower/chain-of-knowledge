import openai
import os


import requests
import json

HTTP_LLM_API_KEY='eyJ0eXAiOiJqd3QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IjM5NDc3MyIsInBhc3N3b3JkIjoiMzk0NzczMTIzIiwiZXhwIjoyMDIxNjE4MzE3fQ.oQx2Rh-GJ_C29AfHTHE4x_2kVyy7NamwQRKRA4GPA94'
OPENAI_API_KEY='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'

try:
	import dashscope
except ImportError:
	dashscope = None
 
import time

# def get_response(query, model="gpt-4"):
#     url = "http://47.88.8.18:8088/api/ask"
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Bearer xxxxxx"
#     }
#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": query}],
#         "n": 1,
#         "temperature": 0.0
#     }
#     response = requests.post(url, json=data, headers=headers)
#     return response.json()

def call_openai_api(model, input_text, max_tokens=256, temperature=0.0, n=1):
    openai.api_key = OPENAI_API_KEY
    error_times = 0
    
    while error_times < 5:
        try:
            if "text-davinci" in model:
                # InstructGPT models, text completion
                response = openai.Completion.create(
                    model=model,
                    prompt=input_text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n,
                )
                return [response, response["choices"][0]["text"]]
            elif "gpt-3.5" in model:
                # ChatGPT models, chat completion
                response = openai.ChatCompletion.create(
                    model=model,
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": input_text}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=n,
                    timeout=60,
                    request_timeout=60,
                )
                # print(f"response:{response}")
                # exit(0)
                return [response, response["choices"][0]["message"]["content"]]
            
            elif "gpt-4" in model:
                url = "http://47.88.8.18:8088/api/ask"
                headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer " + HTTP_LLM_API_KEY
                            }
                data = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": input_text}
                        ],
                        "n": n,
                        "temperature": temperature
                        }
                response = requests.post(url, json=data, headers=headers)
                response = response.json()
                time.sleep(5)
                new_response = response['data']['response']
                return [new_response, new_response["choices"][0]["message"]["content"]]
            elif model == 'qwen':
                api_key = 'sk-94d038e92230451a87ac37ac34dd6a8a'
                dashscope.api_key = api_key
                response = dashscope.Generation.call(
			        model='qwen-max',
			        messages=[
					        {"role": "system", "content": "You are a helpful assistant."},
					        {"role": "user", "content": input_text}
				        ],
			        result_format="message",  # set the result to be "message" format.
		        )
                time.sleep(5)
                new_response = response.output
                return [new_response, new_response["choices"][0]["message"]["content"]]
            elif model == 'qwen2-57':
                api_key = 'sk-94d038e92230451a87ac37ac34dd6a8a'
                dashscope.api_key = api_key
                response = dashscope.Generation.call(
                model='qwen2-57b-a14b-instruct',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": input_text}
                ],
                result_format="message",  # set the result to be "message" format.
                )
                time.sleep(5)
                new_response = response.output
                return [new_response, new_response["choices"][0]["message"]["content"]]
            elif model == 'llama3-70':
                api_key = 'sk-94d038e92230451a87ac37ac34dd6a8a'
                dashscope.api_key = api_key
                response = dashscope.Generation.call(
                model='llama3-70b-instruct',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": input_text}
                ],
                result_format="message",  # set the result to be "message" format.
                )
                time.sleep(5)
                new_response = response.output
                return [new_response, new_response["choices"][0]["message"]["content"]]
            else:
                raise Exception("Invalid model name")
        except Exception as e:
            print('Retry due to:', e)
            error_times += 1
            continue
        
    return None

