import json
import os

from bs4 import BeautifulSoup
from aiohttp import ClientSession


from core.providers.base import MusicProvider

SOUNDCLOUD_CLIENT_ID = os.environ.get('SOUNDCLOUD_CLIENT_ID')


class NotFoundError(Exception):
    pass

class SoundCloud(MusicProvider):
    NAME = 'SoundCloud'
    _MUSIC_URL = 'https://soundcloud.com/{}/{}'

    async def get_music_name(self, url):
        async with ClientSession() as session:
            async with session.get(url=url) as response:
                soundcloud_page = await response.text()
                soup = BeautifulSoup(soundcloud_page, 'html.parser')
                title_and_artist_tag = soup.find('title')

                if title_and_artist_tag:
                    song_info = title_and_artist_tag.text.split('|')[0]
                    artist_and_title = song_info.split(' by ')[0]

                    # it is my observation, could be just some garbage in the name
                    if len(artist_and_title) > 40:
                        title = artist_and_title.split(' - ')[1]
                        return f'{title}'
                    return f'{artist_and_title}'

    async def get_music_url(self, name):
        print('soundcloud', name)
        api_url = 'https://api-v2.soundcloud.com/search'
        params = {
            'q': name,
            'client_id': SOUNDCLOUD_CLIENT_ID,
            'limit': 1,
        }
        async with ClientSession() as session:
            async with session.get(url=api_url, params=params) as response:
                data = await response.read()
                response.raise_for_status()
                data_json = json.loads(data)

                if data_json:
                    user = data_json['collection'][0]['user']['permalink']
                    track_link = data_json['collection'][0]['permalink']
                    url = self._MUSIC_URL.format(user, track_link)
                    return url
        raise NotFoundError

    @classmethod
    def is_music_url(self, url):
        if 'soundcloud' in url:
            return True

        return False
