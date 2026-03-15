import logging
import os
from dotenv import load_dotenv

from telegram.ext import Application

from handlers.add_cost import cost_handler
from handlers.supermarkt_handler import supermarkt_handler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CSV_PATH = os.environ["EXCEL_PATH"]


def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.bot_data["CSV_PATH"] = CSV_PATH

    application.add_handler(cost_handler)
    application.add_handler(supermarkt_handler)

    application.run_polling()


if __name__ == "__main__":
    main()