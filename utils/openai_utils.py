import openai
import os


import requests
import json


 
import time

HTTP_LLM_API_KEY = os.getenv("HTTP_LLM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")


def call_openai_api(model, input_text, max_tokens=256, temperature=0.0, n=1):
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
                dashscope.api_key = DASHSCOPE_API_KEY
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
                dashscope.api_key = DASHSCOPE_API_KEY
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
                dashscope.api_key = DASHSCOPE_API_KEY
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

