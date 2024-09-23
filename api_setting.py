import openai
import time
from queue import Queue
import requests
import json
from utils.format_tokens import *
# import torch
from PIL import Image
# from transformers import AutoModelForCausalLM, LlamaTokenizer, AutoTokenizer
import argparse
# from transformers.generation import GenerationConfig
from utils.format_tokens import append_to_jsonl
from gradio_client import Client

openai_keys = [
    # FILL HERE
]
api_base_url = "https://api.openai.com/v1"

class API:
    def __init__(self,temperature = 0.0) -> None:
        self.t = temperature
        self.client = openai.OpenAI(api_key='', base_url=api_base_url)
        self.key_queue = Queue()
        for k in openai_keys:
            self.key_queue.put(k)

    def models(self):
        k = self.key_queue.get()
        self.client.api_key = k

        return self.client.models.list().data

    def ChatCompletion(self,model,messages,temperature=None,**kwargs) -> str:
        if temperature == None:
            temperature = self.t
        key = self.key_queue.get()

        retry_count = 3
        retry_interval = 0.5

        errormsg=''
        for _ in range(retry_count):
            try:
                self.client.api_key = key
                response = self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=temperature,
                            **kwargs
                        )
                reply = response.choices[0].message.content
                if reply == '':
                    raise ValueError('EMPTY RESPONSE CONTENT')
                # After success request, return the key
                self.key_queue.put(key)
                return reply

            except (openai.RateLimitError,openai.APIError,openai.OpenAIError,openai.PermissionDeniedError) as e:
                if "quota" in e.message or "exceeded" in e.message or "balance" in e.message: # type: ignore
                    # Discard the old one and find a new key
                    errormsg=e
                    with open('RanOutKeys.txt','a') as f:
                        f.write(f'{key}\n')
                    key = self.key_queue.get()
                else:
                    errormsg=e
                    retry_interval *= 5
                    # cool down time
                    time.sleep(retry_interval)
            except (ValueError,Exception) as e:
                errormsg=e
                retry_interval *= 5
                # cool down time
                time.sleep(retry_interval)
        # Repeated retry failed to return the key
        self.key_queue.put(key)
        raise ConnectionError(f"ChatCompletion Retries Failure {key[-5:]}-{errormsg}")

    def dummyChat(self):
        key = self.key_queue.get()
        print(f"Dummy get [{key[-5:]}] at {time.time()}")
        self.key_queue.put(key)

class vllmAPI:
    def __init__(self, args) -> None:
        self.api_url = f"http://{args.host}:{args.port}/generate"

    def post_http_request(self, prompt, args) -> requests.Response:
        headers = {"User-Agent": "Test Client"}
        pload = {
            "prompt": prompt,
            "n": 1,
            "use_beam_search": False,
            "stop": ["<|im_end|>","</s>","[/INST]","<|user|>","<|assistant|>","<reserved_106>","<reserved_107>"],
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            # "stream": stream,
        }
        response = requests.post(self.api_url, headers=headers, json=pload)
        return response
    
    def ChatCompletion(self, messages, args) -> str:
        if temperature == None:
            temperature = self.t
        # print(f"{prompt}\n", flush=True)
        if isinstance(messages,list) and isinstance(messages[0],dict):
            # prompt = '\n\n'.join([m['content']for m in messages])
            # print(messages)
            if 'yi' in args.model:
                prompt = format_tokens_yi(dialog=messages)
            elif 'mistral' in args.model or 'mixtral' in args.model:
                prompt = format_tokens_mistral(dialog=messages)
            elif 'phi' in args.model:
                prompt = format_tokens_phi(dialog=messages)
            elif 'chatglm' in args.model:
                prompt = format_tokens_chatglm(dialog=messages)
            elif 'qwen' in args.model:
                prompt = format_tokens_qwen(dialog=messages)
            elif 'baichuan2' in args.model:
                prompt = format_tokens_baichuan(dialog=messages)
            else:
                prompt = format_tokens_llama(dialog=messages)
            # print(prompt)
        else:
            prompt = str(messages)
        # print(f"[USER] {prompt}\n")
        for _ in range(3):
            response = self.post_http_request(prompt, args)
            if response.status_code == 200:
                # Reply is the completion of prompt, so delete the previous prompt in reply.
                reply = json.loads(response.content)["text"][0].removeprefix(prompt).strip()
                # print(f"{color(reply,'YELLOW')}")
                return reply
        raise ConnectionError('SERVER DO NOT RESPOND')

def local_generate_cogagent(prompt, image, args):
    client = Client("http://127.0.0.1:7860/")
    result = client.predict(
            prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
            image,	# str  in 'path of the image' Textbox component
            1,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
            True,	# bool  in 'do_sample' Checkbox component
            0.01,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
            1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
            0,	# float (numeric value between 0 and 200) in 'top_k' Slider component
            0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
            0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
            1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
            0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
            -5,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
            True,	# bool  in 'early_stopping' Checkbox component
            "",	# str  in 'Groud truth' Textbox component
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_autoui(prompt, image, args):
    client = Client(f"http://127.0.0.1:{args.port}/")
    result = client.predict(
            prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
            image,	# str  in 'path of the image' Textbox component
            1,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
            True,	# bool  in 'do_sample' Checkbox component
            0.01,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
            1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
            0,	# float (numeric value between 0 and 200) in 'top_k' Slider component
            0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
            0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
            1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
            0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
            -5,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
            True,	# bool  in 'early_stopping' Checkbox component
            "",	# str  in 'Groud truth' Textbox component
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_qwenvl(prompt, image, args):
    client = Client("http://127.0.0.1:7860/")
    result = client.predict(
            prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
            image,	# str  in 'path of the image' Textbox component
            1,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
            True,	# bool  in 'do_sample' Checkbox component
            0.01,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
            0,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
            1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
            0,	# float (numeric value between 0 and 200) in 'top_k' Slider component
            0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
            0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
            1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
            0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
            -5,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
            True,	# bool  in 'early_stopping' Checkbox component
            "",	# str  in 'Groud truth' Textbox component
            api_name="/textgen"
    )
    print(result[0])
    return result[0]

def local_generate_yivl(prompt, image, args):
    client = Client("http://127.0.0.1:8111/")
    result = client.predict(
        prompt,	# str  in 'parameter_3' Textbox component
        image,	# filepath  in 'parameter_9' Image component
        "Crop",	# Literal['Crop', 'Resize', 'Pad', 'Default']  in 'Preprocess for non-square image' Radio component
        api_name="/add_text"
    )
    result = client.predict(
		0.2,	# float (numeric value between 0.0 and 1.0) in 'Temperature' Slider component
		0.7,	# float (numeric value between 0.0 and 1.0) in 'Top P' Slider component
		128,	# float (numeric value between 0 and 1024) in 'Max output tokens' Slider component
        api_name="/predict"
)
    print(result)
    return result[0]

def local_general_llava(data, args):
    pass
# if __name__ == '__main__':
#     message = [{'role':'system','content':'You are my maid.'},
#                {'role':'user','content':'How is the weather today?'},
#                {'role':'assistant','content':'A bright sunny day, sir.'},
#                 {'role':'user','content':'What is my schedule today?'},
#                ]
#     print(vllmApi.ChatCompletion('gpt-3.5-turbo-1106',message, 0.0))

#     print(vllmApi.ChatCompletion('gpt-4-0125-preview',message, temperature=0.0))
