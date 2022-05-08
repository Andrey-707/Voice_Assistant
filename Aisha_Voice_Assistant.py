# Voice_Assistant.
from colorama import init, Fore, Back, Style # цвет текста терминала
import os # модуль системы
import time # модуль времени
import speech_recognition as sr # голосовые модули
from fuzzywuzzy import fuzz
import pyttsx3
import datetime # модуль дата/время
import pyowm # модули погоды OpenWeatherMap
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
import requests # запрос с сайта
import sys # выход из программы
import config # для работы с погодой


# Функции
def speak(what):
    print( what )
    speak_engine = pyttsx3.init()
    speak_engine.say (what)
    speak_engine.runAndWait()
    speak_engine.stop()


def callback(recognizer, audio):    
    try:
        voice = recognizer.recognize_google(audio, language = "ru-RU").lower()
        print("[log] Распознано: " + voice)
        if voice.startswith(opts["alias"]):
            # обращаются к Боту
            cmd = voice
            for x in opts['alias']:
                cmd = cmd.replace(x, "").strip()
            for x in opts['tbr']:
                cmd = cmd.replace(x, "").strip()
            # распознаем и выполняем команду
            cmd = recognize_cmd(cmd)
            execute_cmd(cmd['cmd'])
    except sr.UnknownValueError:
        print("[log] Голос не распознан!")
    except sr.RequestError as e:
        print("[log] Неизвестная ошибка, проверьте интернет!")


def recognize_cmd(cmd):
    RC = {'cmd': '', 'percent': 80}
    for c,v in opts['cmds'].items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > RC['percent']:
                RC['cmd'] = c
                RC['percent'] = vrt
    return RC


def choose_plural(amount, variants):
    '''Функция выбора формы существительного
    для корректного поизношения времени и температуры'''
    if amount % 10 == 1 and amount % 100 != 11:
        variant = 0
    elif amount % 10 >= 2 and amount % 10 <= 4 and \
            (amount % 100 < 10 or amount % 100 >= 20):
        variant = 1
    else:
        variant = 2
    return '{} {}'.format(amount, variants[variant])


def execute_cmd(cmd):
    if cmd == 'ctime':
        now = datetime.datetime.now()
        speak("Сейчас  " + str(choose_plural(now.hour, ('час', 'часа', 'часов'))) + 
            " : " + str(choose_plural(now.minute, ('минута', 'минуты', 'минут'))))

    elif cmd == 'weather':
        # вывод погоды на экран
        path1 = config.weatherpath
        os.system(path1)
        # сказать текущую погоду
        speak("Температура сейчас " + 
            str(choose_plural(temp, ('градус', 'градуса', 'градусов'))))
        # анализ данных температуры
        if temp < -4:
            speak("Сейчас на улице морозно.")
        elif temp < 0 and temp >= -4:
            speak("Сейчас на улице холодно.")
        elif temp >= 0 and temp < 12:
            speak("Сейчас на улице прохладно.")
        elif temp >= 12 and temp < 27:  
            speak("Сейчас на улице тепло.")
        else: # temp > 27
            speak("Сейчас на улице жарко.")

    elif cmd == 'winamp':
        # воспроизвести !!!ПЛЕЙЛИСТ!!! в winamp
        speak("Включаю...")
        # открывает плейлист, который создан через winamp и сохранен по данному адресу
        path2 = config.playlist
        os.system(path2)        
    elif cmd == 'funny1':
        # как дела, робот?
        speak("Сам ты робот. Я живая...")  
    elif cmd == 'funny2':
        # рассказать анекдот
        speak("Мой разработчик не научил меня анекдотам...")
    elif cmd == 'wisdom1':
        # рассказать народную мудрость
        speak("Лучше больше, да лучше...")
    elif cmd == 'wisdom2':
        # рассказать народную мудрость
        speak("Сэкономил - значит заработал...")
    elif cmd == 'funny':
        # хвалю
        speak("Спасибо, ты тоже ничего")
    elif cmd == 'exit':
        # выходим из программы
        speak("Выход из программы!")
        sys.exit()
    else:
        print('Команда не распознана, повторите!')

# запуск
r = sr.Recognizer()
m = sr.Microphone(device_index=1)

with m as source:
    r.adjust_for_ambient_noise(source)

speak_engine = pyttsx3.init()

# если установлен голосовой пакет для синеза речи 
voices = speak_engine.getProperty('voices')
speak_engine.setProperty('voice', voices[2].id)

# погода
config_dict = get_default_config()
config_dict['language'] = 'ru'  # Язык интерпретатора
API = config.API
owm = OWM(API, config_dict)

owm.supported_languages
mgr = owm.weather_manager()

place = config.city
observation = mgr.weather_at_place(place)
w = observation.weather

# Подробный статус
DS = w.detailed_status
# Ветер
wind = w.wind()["speed"]
# Влажность
humidity = w.humidity
# Температура
temp = w.temperature('celsius')["temp"]
# Осадки
rain = w.rain
# Индекс тепла (непонятная величина)
HI = w.heat_index
# Облачнось
clouds = w.clouds

# bot options
opts = {
    "alias": ('аиша','алиса','ариша','париж','тайшет','а еще','а ещё','польша','аяша','алиша'),
    "tbr": ('скажи','расскажи','покажи','сколько','произнеси','включи','ты', 'выполнить'),
    "cmds": {
        "ctime": ('текущее время','сейчас времени','который час','сколько время','время'),
        "weather": ('какая сегодня погода','погода на сегодня','погоду'),
        "funny1": ('как дела робот','как дела robot'),     
        "funny2": ('анекдот','ты знаешь анекдоты'),
        "wisdom1": ('народную мудрость','народная мудрость'),
        "wisdom2": ('другую народную мудрость','другая народная мудрость'),  
        "winamp": ('винамп','винам','winamp','v-nand'),
        "funny": ('молодец','маладец'),
        "exit": ('выход', 'закрыть программу')        
    }
} 

init()

print(Fore.WHITE)
print("Program start")

print(Fore.YELLOW)
speak("Бот активирован...")

# запуск бота в бесконечный цикл
while True:
    with m as source:
        audio = r.listen(source)

    callback(r, audio)
    time.sleep(0.1)