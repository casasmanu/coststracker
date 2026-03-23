from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with options"""
    reply_keyboard = [['/cost', '/market']]
    await update.message.reply_text(
        'Welcome to the cost tracking bot. Choose an option:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=False,
            resize_keyboard=True
        ),
    )


start_handler = CommandHandler("start", start)