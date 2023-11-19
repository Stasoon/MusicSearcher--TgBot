from abc import ABC, abstractmethod


class VkItem(ABC):

    @abstractmethod
    def from_json(self, item):
        pass

    @abstractmethod
    def to_dict(self):
        return self.__dict__
