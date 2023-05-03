import nonebot
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    speech_key = ""
    speech_region = ""

global_config = nonebot.get_driver().config
config = Config(**global_config.dict())

