# -*- coding: utf-8 -*-
import pymorphy2
import requests
from vkbottle import Keyboard, Text, KeyboardButtonColor, Bot
from vkbottle.bot import Message
from hdrezka import Search

bot = Bot(token="vk1.a.D9m0LF97CUEkrtsHqEMmW-c3sOGYeUKA91W_11Y7_NS0umJXp6R_hqzg5pryc4QtoTVaSAA666pFrnUqndvAWFmEW1e1NWIAD9hiUAnAErAe7PQTZ_6gzwWLnwjfIOLnHtieAHvh53L82WQpT4Ls8QaHpomUs1e3vbY-APioUX-HO8jXZBccuw77N0T30lVEeKgj7FrA24X92hsbYGyU1Q")

keyboard = Keyboard(one_time=False).add(
    Text(f"Найти фильм", {"menu": "film"}), color=KeyboardButtonColor.POSITIVE
).row().add(
    Text(f"Найти сериал", {"menu": "series"}), color=KeyboardButtonColor.NEGATIVE
).get_json()


@bot.on.private_message(text="Начать")
async def start(message: Message):
    await message.answer("Воспользуйся клавиатурой ниже: ", keyboard=keyboard)


@bot.on.private_message(payload={"menu": "series"})
async def series_start(message: Message):
    await message.answer("Введи название сериала")
    await bot.state_dispenser.set(peer_id=message.from_id, state='series_start')


@bot.on.private_message(payload={"menu": "film"})
async def series_start(message: Message):
    await message.answer("Введи название фильма")
    await bot.state_dispenser.set(peer_id=message.from_id, state='film_start')


def pluralize_noun(word, number):
    morph = pymorphy2.MorphAnalyzer()

    parsed_word = morph.parse(word)[0]
    pluralized_word = parsed_word.make_agree_with_number(number).word

    return pluralized_word


async def parse_video(player, translator_id, season=None, episode=None):
    try:
        if season is not None and episode is not None:
            link = (await player.get_stream(season=season, episode=episode, translator_id=translator_id)).video
        else:
            link = (await player.get_stream(translator_id=translator_id)).video
        return link
    except Exception as e:
        return e


async def send_quality_options(message, link_qualities, payload_key):
    keyboard3 = Keyboard(inline=True)
    for i, quality in enumerate(link_qualities, start=1):
        keyboard3.add(Text(quality, payload={payload_key: "quality"}))
        if i % 2 == 0:
            keyboard3.row()
    await message.answer("Выбери качество ниже:", keyboard=keyboard3)


async def handle_error(message, e):
    if e == 'httpx.ConnectTimeout':
        await message.answer("Ошибка со стороны бота, попробуй ещё раз")
    else:
        await message.answer(f"Произошла неизвестная ошибка: {e}", keyboard=keyboard)


@bot.on.private_message(payload={"quality": "quality"})
async def series_4(message: Message):
    quality = message.text
    state = await bot.state_dispenser.get(message.from_id)
    if state is not None and state.state == 'series_3':
        link, link_qualities = state.payload['link'], state.payload['link_qualities']
        for link_quality in link_qualities:
            try:
                links = str(link).partition(f"{link_quality}")[2].partition(f"': '")[2].partition(f"', '")[0]
                links = links.partition(":hls:")[0]
                quality_list = {"360p", "480p", "720p", "1080p", "1080p Ultra", "2K", "4K"}
                if quality in quality_list and quality == link_quality:
                    req = (requests.get(links, allow_redirects=False)).headers.get('Location')
                    await message.answer(links, keyboard=keyboard)
                    await message.answer(req, keyboard=keyboard)
            except Exception as e:
                print(e)
                await handle_error(message, e)


@bot.on.private_message(payload={"film": "quality"})
async def series_4(message: Message):
    quality = message.text
    state = await bot.state_dispenser.get(message.from_id)
    if state is not None and state.state == 'film_3':
        link, link_qualities = state.payload['link'], state.payload['link_qualities']
        for link_quality in link_qualities:
            try:
                links = str(link).partition(f"{link_quality}")[2].partition(f"': '")[2].partition(f"', '")[0]
                links = links.partition(":hls:")[0]
                quality_list = {"360p", "480p", "720p", "1080p", "1080p Ultra", "2K", "4K"}
                if quality in quality_list and quality == link_quality:
                    req = (requests.get(links, allow_redirects=False)).headers.get('Location')
                    await message.answer(links, keyboard=keyboard)
                    await message.answer(req, keyboard=keyboard)
            except Exception as e:
                print(e)
                await handle_error(message, e)


@bot.on.private_message(payload={"film": "audio"})
async def series_3(message: Message):
    state = await bot.state_dispenser.get(message.from_id)
    if state is not None and state.state == 'film_2':
        player, audio_list = state.payload['player'], state.payload['audio_list']
        try:
            link = await parse_video(player, audio_list[message.text])
            link_qualities = link.qualities
            await send_quality_options(message, link_qualities, "film")
            await bot.state_dispenser.set(peer_id=message.from_id, state='film_3', player=player,
                                          audio_list=audio_list, link_qualities=link_qualities, link=link)
        except Exception as e:
            await handle_error(message, e)


@bot.on.private_message(payload={"audio": "audio"})
async def series_3(message: Message):
    state = await bot.state_dispenser.get(message.from_id)
    if state is not None and state.state == 'series_2':
        player, season, episode, audio_list = state.payload['player'], state.payload['season'], state.payload['episode'], state.payload['audio_list']
        try:
            link = await parse_video(player, audio_list[message.text], season=season, episode=episode)
            link_qualities = link.qualities
            await send_quality_options(message, link_qualities, "quality")
            await bot.state_dispenser.set(peer_id=message.from_id, state='series_3', season=season,
                                          episode=episode, player=player, audio_list=audio_list,
                                          link_qualities=link_qualities, link=link)
        except Exception as e:
            print(e)
            await handle_error(message, e)


@bot.on.private_message(text="<text>")
async def series_2(message: Message, text):
    global name, season
    state = await bot.state_dispenser.get(message.from_id)
    if state is not None and state.state == 'series_start':
        name = text
        await message.answer("Введи сезон")
        await bot.state_dispenser.set(peer_id=message.from_id, state='series_season')
    elif state is not None and state.state == 'film_start':
        name_film = text
        try:
            player = await (await Search(f'{name_film}').get_page(1))[0].player
        except Exception as e:
            await message.answer("Фильм не найден либо произошла ошибка, попробуй ещё раз")
            return
        audio, a, audio_list = '', 0, {}
        keyboard2 = Keyboard(inline=False, one_time=True)
        count = 0
        for translator_name, translator_id in player.post.translators.name_id.items():
            link = await parse_video(player, translator_id)
            if str(link).startswith("Время сессии истекло.") or not str(link).startswith("VideoURLs"):
                continue
            a += 1
            if a % 3 == 0:
                keyboard2.row()
            audio_list[translator_name] = translator_id
            keyboard2.add(Text(translator_name, payload={"film": "audio"}))
            count += 1
        if count == a:
            pass
        else:
            await message.answer("Не удалось получить все озвучки, попробуйте снова")
            return
        if a != 0:
            word = 'озвучка'
            pluralized_word = pluralize_noun(word, a)
            await message.answer(f"Найдено {a} {pluralized_word}, выбери нужную ниже:", keyboard=keyboard2.get_json())
            await bot.state_dispenser.set(peer_id=message.from_id, state='film_2', name=name_film, player=player,
                                          audio_list=audio_list)
        else:
            await message.answer(f"Фильм не найден", keyboard=keyboard)
    elif state is not None and state.state == 'series_season':
        season = text
        await message.answer("Введи эпизод")
        await bot.state_dispenser.set(peer_id=message.from_id, state='series_episode')
    elif state is not None and state.state == 'series_episode':
        episode = text
        try:
            player = await (await Search(f'{name}').get_page(1))[0].player
        except Exception as e:
            await message.answer("Сериал не найден либо произошла ошибка, попробуй ещё раз")
            return
        audio, a, audio_list = '', 0, {}
        keyboard2 = Keyboard(inline=False, one_time=True)
        count = 0
        for translator_name, translator_id in player.post.translators.name_id.items():
            link = await parse_video(player, translator_id, season=season, episode=episode)
            if str(link).startswith("Время сессии истекло.") or not str(link).startswith("VideoURLs"):
                continue
            a += 1
            if a % 3 == 0:
                keyboard2.row()
            audio_list[translator_name] = translator_id
            keyboard2.add(Text(translator_name, payload={"audio": "audio"}))
            print(translator_name, link[0])
            count += 1
        if count == a:
            pass
        else:
            await message.answer("Не удалось получить все озвучки, попробуйте снова")
            return
        if a != 0:
            word = 'озвучка'
            pluralized_word = pluralize_noun(word, a)
            await message.answer(f"Найдено {a} {pluralized_word}, выбери нужную ниже:", keyboard=keyboard2.get_json())
            await bot.state_dispenser.set(peer_id=message.from_id, state='series_2', name=name, season=season,
                                          episode=episode, player=player, audio_list=audio_list)
        else:
            await message.answer(f"Сериал/Сезон/Эпизод не найден", keyboard=keyboard)

bot.run_forever()
