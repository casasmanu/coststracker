import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from states import (
    SUPERMARKET_NAME,
    SUPERMARKET_ACTION,
    SUPERMARKET_PRODUCT,
    SUPERMARKET_PRODUCT_PRICE,
    SUPERMARKET_PRODUCT_QUALITY,
)

from interfaces.excel_driver import update_excel, read_data

logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def start_supermarket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation to check supermarket info"""

    context.user_data.clear()

    reply_keyboard = [['EDEKA', 'PENNY', 'REWE', 'OTHER']]

    await update.message.reply_text(
        '<b>Welcome to the price tracker bot\n'
        'This is a simple homemade tool, so expect rough edges\n'
        'Which supermarket do you want to check?</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    return SUPERMARKET_NAME


async def select_supermarket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Read the supermarket name and ask for action"""

    context.user_data['supermarket'] = update.message.text

    reply_keyboard = [['Read List', 'Add Price']]

    await update.message.reply_text(
        "Select desired action",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    return SUPERMARKET_ACTION


async def select_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Choose between reading list or adding product"""

    desired_action = update.message.text

    if desired_action == "Read List":

        selected_supermarket = context.user_data["supermarket"]

        supermarket_data = read_data(path=context.bot_data["CSV_PATH"], sheet_name=selected_supermarket)

        await update.message.reply_text(
            supermarket_data,
        )

        await update.message.reply_text(
            "What would you like to do now?",
            reply_markup=ReplyKeyboardMarkup(
                [['/cost', '/market'], ['/latest', '/total'], ['/delete', '/help']],
                one_time_keyboard=False,
                resize_keyboard=True
            ),
        )

        return ConversationHandler.END

    elif desired_action == "Add Price":

        await update.message.reply_text(
            "Please enter the Product name to be added to the list",
            reply_markup=ReplyKeyboardRemove(),
        )

        return SUPERMARKET_PRODUCT

    else:

        await update.message.reply_text(
            "Invalid option. Please choose again."
        )

        return SUPERMARKET_ACTION


async def receive_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores product name"""

    context.user_data["product"] = update.message.text

    await update.message.reply_text(
        "Now enter the price",
    )

    return SUPERMARKET_PRODUCT_PRICE


async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores product price"""

    try:
        price = float(update.message.text)
        context.user_data["price"] = price
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the price."
        )
        return SUPERMARKET_PRODUCT_PRICE

    await update.message.reply_text(
        "Add some quality description",
    )

    return SUPERMARKET_PRODUCT_QUALITY


async def save_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores quality and writes to Excel"""

    context.user_data["supermarket_extra"] = update.message.text

    super_name = context.user_data["supermarket"]
    product = context.user_data["product"]
    price = context.user_data["price"]
    extra = context.user_data["supermarket_extra"]

    success = update_excel(
        path=context.bot_data["CSV_PATH"],
        sheet_name=super_name,
        sheet_columns=["Product", "Price", "Quality"],
        sheet_data=[product, price, extra],
    )

    if success:
        await update.message.reply_text(
            "Thanks! Price successfully added.",
        )
    else:
        await update.message.reply_text(
            "Error while saving the product.",
        )

    await update.message.reply_text(
        "What would you like to do now?",
        reply_markup=ReplyKeyboardMarkup(
            [['/cost', '/market'], ['/latest', '/total'], ['/delete', '/help']],
            one_time_keyboard=False,
            resize_keyboard=True
        ),
    )

    return ConversationHandler.END


supermarket_handler = ConversationHandler(
    entry_points=[CommandHandler("market", start_supermarket)],
    states={
        SUPERMARKET_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_supermarket)
        ],
        SUPERMARKET_ACTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_action)
        ],
        SUPERMARKET_PRODUCT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_product)
        ],
        SUPERMARKET_PRODUCT_PRICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price)
        ],
        SUPERMARKET_PRODUCT_QUALITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_product)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)