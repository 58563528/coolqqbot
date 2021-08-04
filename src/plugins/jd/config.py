from nonebot import get_driver
from pydantic import BaseSettings

from src.utils.plugin import PluginData

DATA = PluginData('jd', config=True)


class Config(BaseSettings):
    cdTime: int = int(DATA.get_config('jd', 'cdTime', fallback='60'))
    group_id: int = int(DATA.get_config('jd', 'group_id', fallback='30'))
    class Config:
        extra = 'ignore'


global_config = get_driver().config
plugin_config = Config(**global_config.dict())
