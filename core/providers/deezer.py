import requests
import json
import asyncio
from aiohttp import ClientSession
from core.providers.base import MusicProvider


class Deezer(MusicProvider):
    NAME = 'Deezer'
    _MUSIC_URL = 'http://www.deezer.com/track/{}'

    async def get_music_name_async(self, url):
        api_url = 'http://api.deezer.com/track/{}'

        params = {
            'id': self.__id_from_url(url),
            'entity': 'song'
        }
        async with ClientSession() as session:
            async with session.get(url=api_url, params=params) as response:
                data = await response.read()
                data_json = json.loads(data)
                response.raise_for_status()
                if data_json:
                    return f'{data_json["artist"]["name"]} - {data_json["title"]}'
        return None

    async def get_music_url_async(self, name):
        print('dezeer', name)
        api_url = 'http://api.deezer.com/search/track'
        params = {
            'q': name,
            'index': 0,
            'limit': 1,
            'output': 'json'
        }
        async with ClientSession() as session:
            async with session.get(url=api_url, params=params) as response:
                data = await response.read()
                response.raise_for_status()
                data_json = json.loads(data)

                track_id = data_json['data'][0]['id']
                url = self._MUSIC_URL.format(track_id)
                return url

    @staticmethod
    def __id_from_url(url):
        id_search = url.split('/')[-1]
        return id_search

    @classmethod
    def is_music_url(self, url):
        if 'deezer' in url:
            return True

        return False
