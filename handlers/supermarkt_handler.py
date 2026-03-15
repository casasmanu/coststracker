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
    SUPERMARKT_NAME,
    SUPERMARKT_ACTION,
    SUPERMARKT_PRODUCT,
    SUPERMARKT_PRODUCT_PRIZE,
    SUPERMARKT_PRODUCT_QUALITY,
)

from interfaces.drvExcel import updateExcel, readData

logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def supermarkt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts conversation to check supermarket info"""

    reply_keyboard = [['EDEKA', 'PENNY', 'REWE', 'OTRO']]

    await update.message.reply_text(
        '<b>Bienvenido al bot ayudamemoria de precios\n'
        'Es super casero asi que no creas que va a funcionar bien\n'
        'que supermercado queres revisar?</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    return SUPERMARKT_NAME


async def supermarkt_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Read the supermarket name and ask for action"""

    context.user_data['supermarket'] = update.message.text

    reply_keyboard = [['Read List', 'ADD Prize']]

    await update.message.reply_text(
        "Select desired action",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    return SUPERMARKT_ACTION


async def supermarkt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Choose between reading list or adding product"""

    desired_action = update.message.text

    if desired_action == "Read List":

        selected_supermarkt = context.user_data["supermarket"]

        supermarkt_data = readData(path=context.bot_data["CSV_PATH"],sheetName=selected_supermarkt)

        await update.message.reply_text(
            supermarkt_data,
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END

    elif desired_action == "ADD Prize":

        await update.message.reply_text(
            "Please enter the Product name to be added to the list",
            reply_markup=ReplyKeyboardRemove(),
        )

        return SUPERMARKT_PRODUCT

    else:

        await update.message.reply_text(
            "Invalid option. Please choose again."
        )

        return SUPERMARKT_ACTION


async def supermarkt_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores product name"""

    context.user_data["product"] = update.message.text

    await update.message.reply_text(
        "Now enter the price",
        reply_markup=ReplyKeyboardRemove(),
    )

    return SUPERMARKT_PRODUCT_PRIZE


async def supermarkt_prize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores product price"""

    context.user_data["prize"] = update.message.text

    await update.message.reply_text(
        "Add some quality description",
        reply_markup=ReplyKeyboardRemove(),
    )

    return SUPERMARKT_PRODUCT_QUALITY


async def supermarkt_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores quality and writes to Excel"""

    context.user_data["supermarkt_extra"] = update.message.text

    super_name = context.user_data["supermarket"]
    product = context.user_data["product"]
    prize = context.user_data["prize"]
    extra = context.user_data["supermarkt_extra"]

    updateExcel(
        path=context.bot_data["CSV_PATH"],
        sheetName=super_name,
        sheet_columns=["Producto", "Precio", "Calidad"],
        sheet_data=[product, prize, extra],
    )

    await update.message.reply_text(
        "Thanks! Price successfully added.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


supermarkt_handler = ConversationHandler(
    entry_points=[CommandHandler("Super", supermarkt_start)],
    states={
        SUPERMARKT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, supermarkt_name)
        ],
        SUPERMARKT_ACTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, supermarkt_action)
        ],
        SUPERMARKT_PRODUCT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, supermarkt_product)
        ],
        SUPERMARKT_PRODUCT_PRIZE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, supermarkt_prize)
        ],
        SUPERMARKT_PRODUCT_QUALITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, supermarkt_quality)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)