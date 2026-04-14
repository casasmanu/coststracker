from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes

HELP_TEXT = (
    "<b>Available commands:</b>\n\n"
    "/cost — Add a new expense\n"
    "/market — Check or add supermarket prices\n"
    "/latest — Last 5 expenses (or /latest N for N expenses)\n"
    "/total — Total for current month (or /total N for month N)\n"
    "/delete — Delete the last registered expense\n"
    "/help — Show this message"
)

MAIN_KEYBOARD = [['/cost', '/market'], ['/latest', '/total'], ['/delete', '/help']]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with options"""
    await update.message.reply_text(
        'Welcome to the cost tracking bot. Choose an option:',
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            one_time_keyboard=False,
            resize_keyboard=True
        ),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands with keyboard"""
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            MAIN_KEYBOARD,
            one_time_keyboard=False,
            resize_keyboard=True
        ),
    )


start_handler = CommandHandler("start", start)
help_handler = CommandHandler("help", help_command)