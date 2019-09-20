from app import create_app
import logging

app = create_app()
ctx = app.app_context()
ctx.push()

from app import telegrambot
from app import googlesheets
from app import routes

ctx.pop()


logger = telegrambot.telebot.logger
telegrambot.telebot.logger.setLevel(logging.INFO)






