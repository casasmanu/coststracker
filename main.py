import logging
import os
from dotenv import load_dotenv

from telegram.ext import Application

from telegram.ext import CommandHandler

from handlers.add_cost import (
    cost_handler,
    show_last_expenses,
    show_monthly_total,
    delete_last_expense_handler,
    show_last_month_expenses,
    show_spending_analysis,
)
from handlers.supermarket_handler import supermarket_handler
from handlers.start_handler import start_handler, help_handler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CSV_PATH = os.environ["EXCEL_PATH"]


def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.bot_data["CSV_PATH"] = CSV_PATH
    application.add_handler(cost_handler)
    application.add_handler(CommandHandler("latest", show_last_expenses))
    application.add_handler(CommandHandler("total", show_monthly_total))
    application.add_handler(CommandHandler("lastmonth", show_last_month_expenses))
    application.add_handler(CommandHandler("analysis", show_spending_analysis))
    application.add_handler(CommandHandler("delete", delete_last_expense_handler))
    application.add_handler(supermarket_handler)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
    
