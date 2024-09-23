from zhipuai import ZhipuAI
from openai import OpenAI
import google.generativeai as genai
from gradio_client import Client
import re, time
from dashscope import MultiModalConversation
import anthropic
import json, requests

class APIclient:
    def __init__(self, args, api_key) -> None:
        self.args = args
        print(self.args.api, self.args.api == 'yi')
        if self.args.api == 'bc':
            self.client = None
        if self.args.api == 'openai':
            self.client = OpenAI(api_key = api_key)
        elif self.args.api == 'zp':
            self.client = ZhipuAI(api_key=" ")
        elif self.args.api == 'gemini':
            self.client = genai.GenerativeModel(self.args.model)
            genai.configure(api_key=' ')
        elif self.args.api == 'qwen' or self.args.api == 'cogagent' or self.args.api == 'llava' or self.args.api == 'autoui' or self.args.api == 'seeclick'or self.args.api == 'fuyu' or self.args.api == 'minicpm':
            self.client = Client(f"http://{self.args.host}:{self.args.port}/")
            # client = Client(f"http://127.0.0.1:7860")
        elif self.args.api == 'yi':
            print('loading Yi')
            self.client = OpenAI(
                        api_key="EMPTY",
                        base_url=f"http://{self.args.host}:{self.args.port}/v1/",
                    )
        else:
            NotImplementedError
            self.client = None
            
    def client_to_call_openai(self, encoded_images, system_prompt, prompt):
        content_image = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_images}"}} # gpt-4v
        response = self.client.chat.completions.create(
            model = self.args.model,
            messages=[{"role": "system", "content": system_prompt},
                {"role": "user", "content": [ {"type": "text", "text": prompt}, content_image ],}],
            max_tokens=self.args.max_tokens,
            )
        # print(response)
        # print(response.choices[0].message.content)
        prd = response.choices[0].message.content
        response_total = prd
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_zp(self, encoded_images, system_prompt, prompt):
        content_image = {"type": "image_url", "image_url": {"url": f"{encoded_images}"}} # glm-4v 
        response = self.client.chat.completions.create(
            model = self.args.model,
            messages=[{"role": "system", "content": system_prompt},
                {"role": "user", "content": [ {"type": "text", "text": prompt}, content_image ],}],
            max_tokens=self.args.max_tokens,
            )
        # print(response)
        print(response.choices[0].message.content)
        prd = response.choices[0].message.content
        response_total = prd
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_qwenapi(self, image, encoded_images, system_prompt, prompt):
        image = 'file://'+image
        messages = [
            # {"role": "system", "content": system_prompt},
            {'role': 'user',
            'content': [
                {'image': image},
                {'text': prompt}]}]
        retry_api = 0
        while 1:
            if retry_api >=5:
                break
            try:
                response = MultiModalConversation.call(model=self.args.model, messages=messages)
                print(response)
                prd = response.output.choices[0].message.content[0]["text"]
                break
            except AttributeError:
                time.sleep(2**retry_api)
                retry_api += 1
            except KeyError:
                prd = response.output.choices[0].message.content[0]["box"]
                break
        response_total = prd
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_qwen(self, image, prompt):
        print(image)
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        print(image)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                128,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        prd = response[0]
        print(prd)
        response_total = prd
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_minicpm(self, image, prompt):
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                128,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        prd = response[0]
        print(prd)
        response_total = prd
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_cogagent(self, image, prompt):
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        print(prompt)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                128,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        # parse: Plan: 1. 2. 3.  Grounded Operation: xxx -> CLICK
        print(response[0])
        # try:
        #     # datai['response'] = response[0].split('Plan:')[1].split('2.')[0].strip() + response[0].split('Grounded Operation:')[1].strip()
        #     datai['response_total'] = response[0].split('Plan')[1].split('2.')[0].strip() 
        #     if 'Grounded Operation:' in response[0]:
        #         datai['response'] = datai['response'] + response[0].split('Grounded Operation:')[1].strip().split('at the box')[0]
        #         ground = response[0].split('->')[1].strip()
        # except:
        #     print(f"Failed to parse {response[0]}")
        response_total = response[0]
        return response_total, response[0]
    
    def client_to_call_seeclick(self, image, prompt):
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        print(prompt)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                128,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        # Action Plan: [DUAL_POINT,STATUS_TASK_COMPLETE] ; 
        # Action Decision: "action_type": "DUAL_POINT", "touch_point": "[0.2463, 0.1245]", "lift_point": "[0.2463, 0.1245]", "typed_text": ""
        print('output: ', response[0])
        response_total = response[0]
        try:
            response_seeclick = eval(response[0])
        except:
            response_seeclick  = (0,0)
        return response_total, response_seeclick
    
    def client_to_call_fuyu(self, image, prompt):
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        print(prompt)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                128,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        # Action Plan: [DUAL_POINT,STATUS_TASK_COMPLETE] ; 
        # Action Decision: "action_type": "DUAL_POINT", "touch_point": "[0.2463, 0.1245]", "lift_point": "[0.2463, 0.1245]", "typed_text": ""
        print(response[0])
        responses = response[0].split('\n')
        for resi in responses:
            if resi != '':
                response_total = resi
                break
        # datai['response_total'] = response[0].strip()
        # datai['response_fuyu'] = eval(response[0])
        return response_total, response_total
    
    def client_to_call_llava(self, image, prompt):
        image =image.replace(self.args.img_path ,self.args.server_datapath)
        print(image, self.args.img_path)
        response = self.client.predict(
                prompt,	# str  in 'input text: <image> Goal, layouts, history' Textbox component
                image,	# str  in 'path of the image' Textbox component
                256,	# float (numeric value between 1 and 2000) in 'max_new_tokens' Slider component
                True,	# bool  in 'do_sample' Checkbox component
                1,	# float (numeric value between 0.01 and 1.99) in 'temperature' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'top_p' Slider component
                1,	# float (numeric value between 0.0 and 1.0) in 'typical_p' Slider component
                1,	# float (numeric value between 1.0 and 4.99) in 'repetition_penalty' Slider component
                50,	# float (numeric value between 0 and 200) in 'top_k' Slider component
                0,	# float (numeric value between 0 and 2000) in 'min_length' Slider component
                0,	# float (numeric value between 0 and 20) in 'no_repeat_ngram_size' Slider component
                1,	# float (numeric value between 1 and 20) in 'num_beams' Slider component
                0,	# float (numeric value between 0 and 5) in 'penalty_alpha' Slider component
                1.05,	# float (numeric value between -5 and 5) in 'length_penalty' Slider component
                True,
                '',
                api_name="/textgen"
        )
        # parse
        prd = response[0]
        response_total = prd
        print('##response: ', prd)
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response
    
    def client_to_call_claud(self, encoded_images, system_prompt, prompt):
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            # model ='claude-3-sonnet-20240229',
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": 'image/jpeg',
                                "data": encoded_images,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        print('claud: ', message)
        response_total = message.content[0].text
        prd = response_total
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response 
    
    def client_to_call_claud_2(self, encoded_images, system_prompt, prompt):
        # print(encoded_images)
        # Skey = " "
        Skey = ' '
        url = "https://api.claude-Plus.top/v1/chat/completions"
        payload = json.dumps({
            "model": "claude-3-5-sonnet-20240620",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_images}", "detail": "low"}}
                    ],
                }
            ]
        })
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {Skey}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        retry = 0
        max_retry = 10
        while retry < max_retry:
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                # 解析 JSON 数据为 Python 字典
                data = response.json()
                # 获取 content 字段的值
                content = data['choices'][0]['message']['content']
                print('claud: ', content)
                break
            except:
                print('error: ', response)
                retry += 1
                time.sleep(min(2**retry, 30))
        response_total = content
        prd = content
        try:
            pattern = r'"action_type":\s*"([^"]+)",\s*"element":\s*"([^"]+)"'
            match = re.search(pattern, prd)
            prd = match.group(1) + ' ' + match.group(2)
        except:
            print(f"Failed to parse {prd}")
        response = prd
        return response_total, response 

    
    def client_to_call(self, image, encoded_images, system_prompt, prompt):
        if self.args.api == 'openai':
            response_total, response = self.client_to_call_openai(encoded_images, system_prompt, prompt)
        if self.args.api == 'gemini':
           pass
        if self.args.api == 'bc':
            pass
        if self.args.api == 'claud':
            response_total, response = self.client_to_call_claud(encoded_images, system_prompt, prompt)
        elif self.args.api == 'zp':
            response_total, response = self.client_to_call_zp(encoded_images, system_prompt, prompt)
        elif self.args.api == 'qwenapi':
            response_total, response = self.client_to_call_qwenapi(image, encoded_images, system_prompt, prompt)
        elif self.args.api == 'qwen':
            # CUDA_VISIBLE_DEVICES=2 python myserver.py
            response_total, response = self.client_to_call_qwen(image, prompt)
        elif self.args.api == 'minicpm':
            # CUDA_VISIBLE_DEVICES=0 python myserver.py 
            response_total, response = self.client_to_call_minicpm(image, prompt)
        elif self.args.api == 'cogagent':
            # CUDA_VISIBLE_DEVICES=3 python myserver.py
            response_total, response = self.client_to_call_cogagent(image, prompt)
        elif self.args.api == 'autoui':
            pass
        elif self.args.api == 'seeclick':
            response_total, response = self.client_to_call_seeclick(image, prompt)
        elif self.args.api == 'fuyu':
            response_total, response = self.client_to_call_fuyu(image, prompt)
        elif self.args.api == 'yi':
            pass
        elif self.args.api == 'llava':
            # CUDA_VISIBLE_DEVICES=0,1 python myserver_dollava.py
            response_total, response = self.client_to_call_llava(image, prompt)
        return response_total, response 
        