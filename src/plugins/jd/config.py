from nonebot import get_driver
from pydantic import BaseSettings

from src.utils.plugin import PluginData

DATA = PluginData('jd')


class Config(BaseSettings):
    cdTime: int = int(DATA.get_config('jd', 'cdtime', fallback='60'))
    QQ_group_id: int = int(DATA.get_config('jd', 'qq_group_id', fallback=''))
    class Config:
        extra = 'ignore'


global_config = get_driver().config
plugin_config = Config(**global_config.dict())
