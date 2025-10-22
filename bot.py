
import telebot
import requests
from datetime import datetime

# 🔑 ТВОИ КЛЮЧИ
BOT_TOKEN = "7729138192:AAGbC38NEkyDOZj4LODJwKPBujrmPBnnUYE"
OWM_API_KEY = "d9010a2e2bf835990df4f389dc8b44d0"

bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 Эмодзи и иконки для погоды
weather_icons = {
    "clear": "https://cdn-icons-png.flaticon.com/512/6974/6974833.png",
    "clouds": "https://cdn-icons-png.flaticon.com/512/414/414825.png",
    "rain": "https://cdn-icons-png.flaticon.com/512/1163/1163624.png",
    "drizzle": "https://cdn-icons-png.flaticon.com/512/3075/3075858.png",
    "thunderstorm": "https://cdn-icons-png.flaticon.com/512/1146/1146860.png",
    "snow": "https://cdn-icons-png.flaticon.com/512/2315/2315309.png",
    "mist": "https://cdn-icons-png.flaticon.com/512/4005/4005901.png",
}

# 💾 Сохраняем последние города пользователей
user_cities = {}


# 🌤 Получаем погоду по городу
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()
    try:
        temp = round(data["main"]["temp"])
        feels = round(data["main"]["feels_like"])
        desc = data["weather"][0]["description"].capitalize()
        wind = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        # 🕓 Вычисляем локальное время города
        timezone_offset = data.get("timezone", 0)
        ts_local = data.get("dt", int(datetime.utcnow().timestamp())) + timezone_offset
        local_time = datetime.utcfromtimestamp(ts_local)

        # 🗓 Красиво форматируем дату
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        date_str = f"{local_time.day} {months[local_time.month]} {local_time.year}"
        time_str = local_time.strftime("%H:%M")

        icon_key = data["weather"][0]["main"].lower()
        icon_url = weather_icons.get(icon_key, weather_icons["clear"])

        caption = (
            f"📍 {city}\n"
            f"{desc}\n"
            f"🌡 Температура: {temp}°C\n"
            f"🤔 Ощущается как: {feels}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Ветер: {wind} м/с\n\n"
            f"📅 Дата: {date_str}\n"
            f"🕓 Время: {time_str}\n"
        )

        # 👕 Совет по одежде
        if temp >= 25:
            caption += "\n😎 Жарко — футболка и шорты!"
        elif temp >= 15:
            caption += "\n🧥 Тепло, лёгкая куртка или худи подойдёт."
        elif temp >= 5:
            caption += "\n🧣 Прохладно — надень куртку и что-то с длинным рукавом."
        else:
            caption += "\n🥶 Холодно! Тёплая куртка, шапка и перчатки обязательны."

        return icon_url, caption

    except KeyError:
        return None


# 🏁 Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("🌤 Узнать погоду")
    btn2 = telebot.types.KeyboardButton("📍 Мой город")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот, который подскажет погоду и как одеться.\n\n"
        "🔹 Нажми кнопку ниже или просто напиши название города:",
        reply_markup=markup,
    )


# 📩 Обработка всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    text = message.text.strip()

    # Нажал кнопку
    if text == "🌤 Узнать погоду":
        bot.send_message(user_id, "🌆 Напиши город, для которого хочешь узнать погоду.")
        return

    elif text == "📍 Мой город":
        city = user_cities.get(user_id)
        if city:
            weather = get_weather(city)
            if weather:
                icon_url, caption = weather
                bot.send_photo(user_id, icon_url, caption=caption)
            else:
                bot.send_message(user_id, "Не удалось получить погоду 😕")
        else:
            bot.send_message(user_id, "Ты ещё не вводил город 🌆")
        return

    # Считаем, что пользователь ввёл название города
    city = text
    weather = get_weather(city)

    if weather:
        user_cities[user_id] = city  # 💾 запоминаем
        icon_url, caption = weather
        bot.send_photo(user_id, icon_url, caption=caption)
    else:
        bot.send_message(user_id, "😕 Не удалось найти такой город. Попробуй снова.")


print("✅ Бот запущен...")
bot.polling(none_stop=True)

