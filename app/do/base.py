from abc import abstractmethod

from pydantic import BaseModel, ConfigDict


class DOAttributeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @abstractmethod
    def do_to_model(self, **kwargs):
        pass

# 有do 对象之后，一些方法可以附着在do对象上。不然既不能写在vo里，也不能写在po里，最后只能写各种工具方法
