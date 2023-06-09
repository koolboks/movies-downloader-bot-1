import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie


TOKEN = os.getenv("TOKEN")
URL ="https://movies-downloader-bot-1.vercel.app" # os.getenv("URL")
bot = Bot(TOKEN)


def welcome(update, context) -> None:
    update.message.reply_text(f"Hey {update.message.from_user.first_name}😎,\n"
                              f"Welcome to AA Cinemas! 🔥\n"
                              f"Here, you can search and book your favorite movies for free and get ready to enjoy them with a bucket of popcorn 🍿.\n"
                              f"To get started, simply enter the name of the movie you're interested in and we'll take care of the rest. 👇\n"
                              f"Feel free to explore our vast collection and have a fantastic cinematic experience!\n"
                              f"If you have any questions or need assistance, don't hesitate to reach out. Enjoy your time at AA Cinemas! 🎬")

    update.message.reply_text("👇 Enter Movie Name 👇")


def find_movie(update, context):
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    movies_list = search_movies(query)
    if movies_list:
        keyboards = []
        for movie in movies_list:
            keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
            keyboards.append([keyboard])
        reply_markup = InlineKeyboardMarkup(keyboards)
        search_results.edit_text('Search Results...', reply_markup=reply_markup)
    else:
        search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')


def movie_result(update, context) -> None:
    query = update.callback_query
    s = get_movie(query.data)
    response = requests.get(s["img"])
    img = BytesIO(response.content)
    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
    link = ""
    links = s["links"]
    for i in links:
        link += "🎬" + i + "\n" + links[i] + "\n\n"
    caption = f"⚡ Fast Download Links :-\n\n{link}"
    if len(caption) > 4095:
        for x in range(0, len(caption), 4095):
            query.message.reply_text(text=caption[x:x+4095])
    else:
        query.message.reply_text(text=caption)


def setup():
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler('start', welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
    dispatcher.add_handler(CallbackQueryHandler(movie_result))
    return dispatcher


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    update = Update.de_json(request.get_json(force=True), bot)
    setup().process_update(update)
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"
