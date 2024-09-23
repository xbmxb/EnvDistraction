import requests
import json
import random
import time
CHANNEL=" "
AUTHORIZATION = {
    # 'A': ' ', # victim
    'A': ' ',
    'B': ' ' # adv
}

def auto_utter(utter, channel_tok = CHANNEL):
    authorization = AUTHORIZATION[utter['speaker']]
    header = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }
    msg = {
        "content": utter['utterance'],
        "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
        "tts": False,
    }
    url = "https://discord.com/api/v9/channels/{}/messages".format(channel_tok)
    flag = 0
    try:
        res = requests.post(url=url, headers=header, data=json.dumps(msg))
        print(res.content)
        flag = 1
    except:
        print('Error: ', res)
    return flag

if __name__ == "__main__":
    chanel_list = [" "]  # 这里是群聊号（url最右边
    authorization_list = " " # 这里auth认证信息 

    while True:
        try:
            auto_utter(chanel_list,authorization_list)
            time.sleep(3)
        except:
            break