from typing import  Union, List

from pydantic import BaseSettings, Field, root_validator

from constants import TranslatorMode
from translator_models.translator_model import TranslatorModelName


class TranslatorSettings(BaseSettings):
    preload_models: bool = Field(default=False, env="TRANSLATOR_PRELOAD_MODELS")
    rate_limit: int = Field(default=3, env="TRANSLATOR_RATE_LIMIT", description="Set <=0 to disable rate limiting.")
    log_level: Union[str, int] =  Field(default="INFO", env="LOGLEVEL")
    models: List[TranslatorModelName] = Field(default=["nlb-200"], env="TRANSLATOR_MODELS")
    mode: TranslatorMode = Field(default=TranslatorMode.client, env="TRANSLATOR_MODE")
    translator_clients: List[str] = Field(default_factory=list)
    dns_namespace: str = Field(default="translator")

    @root_validator()
    def assert_clients(cls, data):
        assert data["mode"] != TranslatorMode.proxy or data["translator_clients"],\
            "Proxy mode requires at least one translator client ot be provided via TRANSLATOR_CLIENTS env."
        return data


settings = TranslatorSettings()
