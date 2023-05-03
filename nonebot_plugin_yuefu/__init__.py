import requests
from nonebot import get_driver, on_command
from nonebot.typing import T_State
from nonebot.params import ArgStr, CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment
from nonebot import logger

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

voice = on_command("speak", aliases={"府说"}, block=True, priority=4)


def speech_synthesis_to_wave_file(text: str):
    subscription_key = config.SPEECH_KEY
    region = config.SPEECH_REGION
    logger.info(f'KEY：{subscription_key}, REGION:{region}')

    # construct request body in SSML format
    ssml = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'><voice name='zh-CN-YunfengNeural'>" \
           + text + "</voice></speak>"

    headers = {
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "YOUR_RESOURCE_NAME",
        "Authorization": "Bearer " + get_token(subscription_key, region)
    }

    # send the request and get the response
    response = requests.post(
        "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1",
        headers=headers,
        data=ssml.encode('utf-8')
    )

    # check the response
    if response.status_code == 200:
        with open("outputaudio.wav", "wb") as f:
            f.write(response.content)
        logger.info("Speech synthesized for text [{}]".format(text))
    else:
        logger.error("Error synthesizing speech: {}".format(response.text))


def get_token(subscription_key, region):
    # construct request URL and headers
    url = "https://" + region + ".api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key
    }

    logger.info(f"request url:{url}, headers: {headers}")

    # send the request and get the response
    response = requests.post(url, headers=headers)

    # extract token from the response
    if response.status_code == 200:
        logger.info("get token succeed")
        return response.text
    else:
        logger.error("get token failed")
        raise ValueError("Failed to get token: {}".format(response.text))


@voice.handle()
async def _(state: T_State, arg: Message = CommandArg()):
    args = arg.extract_plain_text().strip()
    if args:
        state["words"] = args


@voice.got("words", prompt=f"想要让Bot说什么话呢?")
async def _(state: T_State, words: str = ArgStr("words")):
    global part
    words = words.strip().replace('\n', '').replace('\r', '')
    speech_synthesis_to_wave_file(words)

    # Upload to third-party service
    files = [
        ('sample', (
            'outputaudio.wav', open('outputaudio.wav', 'rb'),
            'audio/wav'))
    ]
    url = "https://u9c50-6a4b59ba.neimeng.seetacloud.com:6443/voiceChangeModel"

    payload = {'fPitchChange': '1',
               'sampleRate': '44100'}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    if response.status_code != 200:
        print(response.text)
    await voice.finish(MessageSegment.record(response.content))
