import asyncio

from core.providers import OUTPUT_PROVIDERS
from core.urls import UrlsExtractor

BOT_RESPONSE = '{music_urls}'
MUSIC_FROMAT = '{name}:\n{urls}'


async def process_message_async(message):
    # returns generator with urls extracted from message
    msg_urls = UrlsExtractor.get_music_urls(message)
    if not msg_urls:
        # no urls found
        return None
    musics_texts = []
    found_songs = {}
    for url in msg_urls:
        name = await url.get_name_async()

        if not name:
            return None

        # if user sent two links to one song we skip 2nd..n
        if found_songs.get(name):
            continue
        found_songs[name] = []

        await get_music_from_providers(url, found_songs[name], name)

        for name, music_urls in found_songs.items():
            musics_texts.append(MUSIC_FROMAT.format(name=name, urls='\n'.join(music_urls)))

    if musics_texts:
        response = BOT_RESPONSE.format(music_urls='\n'.join(musics_texts))
    else:
        response = None

    return response


async def get_music_from_providers(input_url, songs_urls_list, name):

    providers_copy = list(OUTPUT_PROVIDERS)
    input_provider_index = providers_copy.index(type(input_url.provider))
    input_provider = providers_copy.pop(input_provider_index)

    songs_urls_list.append( f'[{input_provider.NAME}]({input_url.url})')

    futures = [provider().get_music_url_async(name) for provider in providers_copy]
    results = await asyncio.gather(*futures, return_exceptions=True)
    for (provider, result) in zip(providers_copy, results):
        # skip results with raised exceptions
        try:
            songs_urls_list.append(f'[{provider.NAME}]({result.replace("’", "")})')
        except AttributeError:
            continue
    return songs_urls_list
