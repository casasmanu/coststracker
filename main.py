import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

from interfaces.drvExcel import updateExcel
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


### read config File
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    destinatary=os.environ['BOT_DESTINATARY']
    CSV_PATH=os.environ['EXCEL_PATH']
    logger.info("Main.py - environment variables loaded")
except:
    logger.error("Main.py - Error while loading init variables from .env")

## my global var
data_entered=[]

# Define states
TOTAL_COST, COST_DESCRIPTION, COST_EXTRA_DESC = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #starts the conversation 

    await update.message.reply_text(
        '<b>ingresa la plata que gastaste en el siguiente orden:\n'
        'Costo - Descripcion - Info Extra\n'
        'para cancelar ingresa \\cancel</b>',
        parse_mode='HTML',
        #reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )

    return TOTAL_COST


async def total_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user entered cost."""
    user = update.message.from_user
    context.user_data['total_cost'] = update.message.text
    logger.info('the user: %s entered a total cost of : %s', user.first_name, update.message.text)
    await update.message.reply_text(
        f'<b>You entered {update.message.text}.\n'
        f'What is the expense description? </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_DESCRIPTION


async def cost_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the cost description"""    
    user = update.message.from_user
    context.user_data['cost_description'] = update.message.text
    logger.info('the user: %s entered a cost description: %s', user.first_name, update.message.text)
    await update.message.reply_text(
        f'<b>You entered {update.message.text}.\n'
        f'please enter an extra description or empty space </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_EXTRA_DESC


async def cost_extra_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user to fill in the mileage or skip."""
    context.user_data['cost_extra_desc'] = update.message.text
    
    global data_entered

    data_entered=context.user_data

    updateExcel(path=CSV_PATH,description=data_entered['cost_description'],cuantity=data_entered['total_cost'],extra=data_entered['cost_extra_desc'])

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOTAL_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, total_cost)],
            COST_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_description)],
            COST_EXTRA_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_extra_desc)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Handle the case when a user sends /start but they're not in a conversation
    application.add_handler(CommandHandler('start', start))

    application.run_polling()


if __name__ == '__main__':
    main()