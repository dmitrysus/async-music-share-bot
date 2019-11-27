import re
import json

from aiohttp import ClientSession

from core.providers.base import MusicProvider


class AppleMusic(MusicProvider):
    NAME = 'Apple Music'
    _ID_REGEX = re.compile(r'\?.*i=([\w]+)')
    _MUSIC_URL = 'https://music.apple.com/us/album/{}/{}?i={}'
    _DOMAINS = ['music.apple', 'itunes.apple']

    async def get_music_name_async(self, url):
        api_url = 'https://itunes.apple.com/lookup'

        params = {
            'id': self.__id_from_url(url),
            'entity': 'song'
        }
        async with ClientSession() as session:
            async with session.get(url=api_url, params=params) as response:
                data = await response.read()
                data_json = json.loads(data)
                response.raise_for_status()

                if data_json['resultCount']:
                    performer = data_json['results'][0]['artistName']
                    title = data_json['results'][0]['trackName']
                    return f'{performer} - {title}'
        return None

    async def get_music_url_async(self, name):
        print('apple', name)
        api_url = 'https://itunes.apple.com/search?'
        params = {
            'term': name,
            'entity': 'song'
        }
        async with ClientSession() as session:
            async with session.get(url=api_url, params=params) as response:
                data = await response.read()
                data_json = json.loads(data)
                response.raise_for_status()

                track_name = re.sub(r"[\(\[].*?[\)\]]", "", data_json['results'][0]['trackName'])
                collection_id = data_json['results'][0]['collectionId']
                track_id = data_json['results'][0]['trackId']
                url = self._MUSIC_URL.format(track_name, collection_id, track_id)
                return url

    def __id_from_url(self, url):
        id_search = self._ID_REGEX.search(url)
        return id_search.group(1)

    @classmethod
    def is_music_url(self, url):
        for domain in self._DOMAINS:
            if domain in url:
                return True

        return False
