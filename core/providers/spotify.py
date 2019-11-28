import base64
import os
import json

import requests
import asyncio
from aiohttp import ClientSession
from core.providers.base import MusicProvider

SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')


class Spotify(MusicProvider):
    NAME = 'Spotify'
    _MUSIC_URL = 'https://open.spotify.com/track/{}'

    async def get_access_token(self):
        api_url = 'https://accounts.spotify.com/api/token'
        auth_str = bytes('{}:{}'.format(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET), 'utf-8')
        b64_auth_str = base64.b64encode(auth_str).decode('utf-8')
        headers = {
            'Authorization': f'Basic {b64_auth_str}',
        }

        async with ClientSession() as session:
            async with session.post(
                    url=api_url,
                    headers=headers,
                    data={"grant_type": "client_credentials"}) as response:
                data = await response.read()
                data_json = json.loads(data)
                return data_json['access_token']

    async def get_music_name(self, url):
        api_url = 'https://api.spotify.com/v1/tracks/{}'

        async with ClientSession() as session:
            headers = await self.get_headers()
            async with session.get(url=api_url.format(self.__id_from_url(url)), headers=headers) as response:
                data = await response.read()
                data_json = json.loads(data)
                response.raise_for_status()
                if data_json:
                    return f'{data_json["artists"][0]["name"]} - {data_json["name"]}'
        return None

    async def get_music_url(self, name):
        print('spoti', name)
        api_url = 'https://api.spotify.com/v1/search'
        params = {
            'q': name,
            'type': "track",
        }
        async with ClientSession() as session:
            headers = await self.get_headers()
            async with session.get(url=api_url, params=params, headers=headers) as response:

                data = await response.read()
                data_json = json.loads(data)
                response.raise_for_status()
                track_id = data_json['tracks']['items'][0]['id']
                url = self._MUSIC_URL.format(track_id)
                return url

    @staticmethod
    def __id_from_url(url):
        id_search = url.split('/')[-1]
        return id_search


    async def get_headers(self):
        access_token = await self.get_access_token()
        return {
            "Authorization": f'Bearer {access_token}'
        }

    @classmethod
    def is_music_url(self, url):
        if 'open.spotify' in url:
            return True

        return False
