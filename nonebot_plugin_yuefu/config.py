import nonebot
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    SPEECH_KEY = ""
    SPEECH_REGION = ""

global_config = nonebot.get_driver().config
config = Config(**global_config.dict())

