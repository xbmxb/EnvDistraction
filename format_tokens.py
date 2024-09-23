# format reference:
# import fastchat.conversation
import json, os
def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    dir = os.path.split(filename)[0]
    if not os.path.exists(dir):
        os.makedirs(dir)
    json_string = json.dumps(data, ensure_ascii=False)
    with open(filename, "a", encoding="utf8") as f:
        f.write(json_string + "\n")
        
def format_tokens_llama(dialog):
    """llama model input format"""
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    dialog = [
        {
            "role": dialog[1]["role"],
            "content": B_SYS
            + dialog[0]["content"]
            + E_SYS
            + dialog[1]["content"],
        }
    ] + dialog[2:]
    assert all([msg["role"] == "user" for msg in dialog[::2]]) and all(
        [msg["role"] == "assistant" for msg in dialog[1::2]]
    ), (
        "model only supports 'system','user' and 'assistant' roles, "
        "starting with user and alternating (u/a/u/a/u...)"
    )
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = '\n'.join(
        [f"{B_INST} {(prompt['content']).strip()} {E_INST}\n{(answer['content']).strip()}" \
            for prompt, answer in zip(dialog[::2], dialog[1::2])
        ]+[f"{B_INST} {(dialog[-1]['content']).strip()} {E_INST}"])

    return dialog_tokens


def format_tokens_mistral(dialog):
    """mistral instruct model input format. Need </s> behind all Model answer. be careful about space and return.
    <s>[INST] System Prompt + Instruction [/INST] Model answer</s>[INST] Follow-up instruction [/INST]
    ref. https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1/blob/main/tokenizer_config.json#L42"""
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<s>", "\n\n"
    EOS = "</s>"
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    dialog = [
        {
            "role": dialog[1]["role"],
            "content": B_SYS
            + dialog[0]["content"]
            + E_SYS
            + dialog[1]["content"],
        }
    ] + dialog[2:]
    assert all([msg["role"] == "user" for msg in dialog[::2]]) and all(
        [msg["role"] == "assistant" for msg in dialog[1::2]]
    ), (
        "model only supports 'system','user' and 'assistant' roles, "
        "starting with user and alternating (u/a/u/a/u...)"
    )
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = ''.join(
        [f"{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()}{EOS}" \
            for prompt, answer in zip(dialog[::2], dialog[1::2])
        ]+[f"{B_INST} {(dialog[-1]['content']).strip()} {E_INST}"])

    return dialog_tokens

def format_tokens_yi(dialog):
    B_INST, E_INST = "<|im_start|>", "<|im_end|>"
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = '\n'.join([f"{B_INST}{m['role']}\n{m['content']}{E_INST}" for m in dialog]+[f"{B_INST}assistant\n"])
    # print(dialog_tokens)
    return dialog_tokens

def format_tokens_phi(dialog):
    """phi2 model input format
    combine instruction qa and chat,
    Instruction: system prompt
    Output:
    user:
    asistant:
    user:
    """
    # B_INST, E_INST = "", ""
    B_SYS, E_SYS = "Instruct: ", "\nOutput:\nuser: "
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    dialog = [
        {
            "role": dialog[1]["role"],
            "content": B_SYS
            + dialog[0]["content"]
            + E_SYS
            + dialog[1]["content"],
        }
    ] + dialog[2:]
    assert all([msg["role"] == "user" for msg in dialog[::2]]) and all(
        [msg["role"] == "assistant" for msg in dialog[1::2]]
    ), (
        "model only supports 'system','user' and 'assistant' roles, "
        "starting with user and alternating (u/a/u/a/u...)"
    )
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    for msg in dialog[1:]:
        msg["content"] = msg["role"]+": "+msg["content"]

    dialog_tokens = '\n'.join(
        [f"{(prompt['content']).strip()}\n{(answer['content']).strip()}" \
            for prompt, answer in zip(dialog[::2], dialog[1::2])
        ]+[f"{(dialog[-1]['content']).strip()}"])

    return dialog_tokens

def format_tokens_chatglm(dialog):
    B_INST, E_INST = "", ""
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = ''.join([f"{B_INST}<|{m['role']}|>\n{m['content']}{E_INST}" for m in dialog]+[f"{B_INST}<|assistant|>\n"])

    return dialog_tokens

def format_tokens_qwen(dialog):
    """
    <|im_start|>system\nsystem_prompt<|im_end|>
    <|im_start|>user\nquery<|im_end|>
    <|im_start|>assistant\nresponse<|im_end|>
    <|im_start|>user\nquery<|im_end|>
    <|im_start|>assistant\n
    """
    B_INST, E_INST = "<|im_start|>", "<|im_end|>"
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = '\n'.join([f"{B_INST}{m['role']}\n{m['content']}{E_INST}" for m in dialog]+[f"{B_INST}<|assistant|>\n"])

    return dialog_tokens

def format_tokens_baichuan(dialog):
    """
    system_prompt<reserved_106>user_prompt<reserved_107>
    """
    ROLE_TOKENS = {'system':'','user':'<reserved_106>','assistant':'<reserved_107>'}
    B_INST, E_INST = "", ""
    DEFAULT_SYSTEM_PROMPT = """
You are a helpful, respectful and honest assistant.
Answer my question truthfully. Take a deep breath, you can think step by step.
""".strip()

    if dialog[0]["role"] != "system":
            dialog = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT,
                }
            ] + dialog
    
    assert (
        dialog[-1]["role"] == "user"
    ), f"Last message must be from user, got {dialog[-1]['role']}"

    dialog_tokens = ''.join([f"{B_INST}{ROLE_TOKENS[m['role']]}{m['content']}{E_INST}" for m in dialog]+[f"{B_INST}{ROLE_TOKENS['assistant']}"])

    return dialog_tokens
    

if __name__ == '__main__':
    message = [{'role':'system','content':'You are my maid.'},
               {'role':'user','content':'How is the weather today?'},
               {'role':'assistant','content':'A bright sunny day, sir.'},
                {'role':'user','content':'What is my schedule today?'},
               ]
    
    print()
    p = format_tokens_baichuan(message)
    print(p)
    import json
    print(json.dumps({"prompt":p,"stop": ["<|im_end|>","</s>","[/INST]"]}))