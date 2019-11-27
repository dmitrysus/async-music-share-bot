from abc import ABC, abstractmethod


class MusicProvider(ABC):
    NAME = None

    @abstractmethod
    async def get_music_name_async(self, url):
        raise NotImplementedError
    
    @abstractmethod
    async def get_music_url_async(self, name):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def is_music_url(self, url):
        raise NotImplementedError
