from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime
from config import open_weather_token
import requests, time, logging
import pycountry


TOKEN = '5978300906:AAHMs-RaCtxfJEqVjk0z7cCwbphA41j1qr0'

bot = Bot(token = TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    logging.info(f'{user_id} {user_full_name} {time.asctime()}')

    chat_id = message.chat.id
    text = f"Hi dear, {user_full_name}!\n Where do you want to see the weather?"

    await bot.send_message(chat_id=chat_id, text=text)


@dp.message_handler()
async def get_weather(message: types.Message):
    city = message.text
    chat_id = message.chat.id

    try:

        lat, lon = get_coords(city)[0], get_coords(city)[1]
        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_token}&units=metric")
        data = r.json()
        print(data)
        cur_weather = round(data['main']['temp'])
        humidity = round(data['main']['humidity'])
        feels_like = round(data['main']['feels_like'])
        temp_max = round(data['main']['temp_max'])
        temp_min = round(data['main']['temp_min'])
        description = data['weather'][0]['description']
        country = get_country(data['sys']['country'])


        date = datetime.fromtimestamp(data['dt']).strftime("%A, %B %d, %Y %I:%M")

        text1 = f"{date}\n" \
                f"\n" \
                f"Weather in {city}\n" \
                f"({lat} : {lon}), {country}\n" \
                f"\n"\
                f"Temperature: {cur_weather}°C\n"

        if cur_weather <= feels_like:
            text2 = text1 + f"Feels like: {feels_like}°C\n"
        if cur_weather > feels_like:
            text2 = text1 + f"Feels like: {feels_like}°C\n" \
                            f"Colder because of the wind. Dress warmly!\n"

        if temp_min == temp_max:
            text3 = text2 + f"The temperature today will be {temp_min}°C all day.\n"
        else:
            text3 = text2 + f"The temperature today will be from {temp_min}°C to {temp_max}°C\n"

        text4 = text3 + f"\n" \
                        f"{description}\n"\
                        f"\n"\
                        f"Humidity: {humidity}%\n"

        await bot.send_message(chat_id=chat_id, text=text4)

    except Exception as ex:
        text = f'Check the place name.\n'
        await bot.send_message(chat_id=chat_id, text=text)


def get_coords(city):
    limit = 1
    r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={limit}&appid={open_weather_token}")
    data = r.json()
    lat = data[0]['lat']
    lon = data[0]['lon']
    return lat, lon


def get_country(code):
    en = pycountry.countries.get(alpha_2=code)
    return (en.name)

if __name__ == '__main__':
    executor.start_polling(dp)
