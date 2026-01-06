import logging
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

from interfaces.drvExcel import updateExcel,readData
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CSV_PATH=""

### read config File
try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CSV_PATH=os.environ['EXCEL_PATH']
    logger.info("Main.py - environment variables loaded")
except:
    logger.error("Main.py - Error while loading init variables from .env")

## my global var
data_entered=[]

# Define states
TOTAL_COST, COST_DESCRIPTION, COST_EXTRA_DESC = range(3)

SUPERMARKT_NAME,SUPERMARKT_ACTION,SUPERMARKT_PRODUCT,SUPERMARKT_PRODUCT_PRIZE,SUPERMARKT_PRODUCT_QUALITY = range(5)
## other posible commands
# retrieve month expenses, add , modify notes.

async def cost_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #starts the conversation 

    await update.message.reply_text(
        '<b>ingresa la plata que gastaste en el siguiente orden:\n'
        'Precio - Nombre - Info Extra\n'
        'para cancelar ingresa \\cancel </b>',
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
    
    product = context.user_data['total_cost']
    description = context.user_data['cost_description'] 
    extra = context.user_data['cost_extra_desc'] 
    
    try:
        updateExcel(path=CSV_PATH,sheet_columns=["Description","Cuantity","Extra"],sheet_data=[product,description,extra])
        await update.message.reply_text(
        f'<b>Data entered correctly\n </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
        )
    
    except Exception as e:
        await update.message.reply_text(
        f'<b>ERROR WHILE ENTERING DATA TO CSV\n ' + e +' </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def supermarkt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    "Starts conversation to check Supermarkts info"
    reply_keyboard = [['EDEKA', 'PENNY', 'REWE', 'OTRO']]

    await update.message.reply_text(
        '<b>Bienvenido al bot ayudamemoria de precios\n'
        'Es super casero asi que no creas que va a funcionar bien\n'
        'que supermercado queres revisar?</b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True),
    )

    ## here would be more usefull to just give the posible supermarket names
    return SUPERMARKT_NAME


async def supermarkt_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    "Read the supermarkt name entered and display the option to choose an action"
    context.user_data['supermarket']=update.message.text

    reply_keyboard = [['Read List', 'ADD Prize']]

    await update.message.reply_text(
        'Select desired action',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

    return SUPERMARKT_ACTION

async def supermarkt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    "Gets supermarket name"
    desired_action=update.message.text

    if desired_action == 'Read List':
        ##Retrieve prizes for the desired supermarkt --> context.user_data['supermarket']
        selected_supermarkt=context.user_data['supermarket']
        supermarkt_data=readData(path=CSV_PATH,sheetName=selected_supermarkt)
        await update.message.reply_text(supermarkt_data, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif desired_action == 'ADD Prize':
        ## add prize to the excel for the desired supermarkt
        await update.message.reply_text(
            'Please enter the Product name to be added to the list',
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove(),
        )

    return SUPERMARKT_PRODUCT


async def supermarkt_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ""
    context.user_data['product']=update.message.text
    await update.message.reply_text(
        'now enter the prize ',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
        )
    return SUPERMARKT_PRODUCT_PRIZE


async def supermarkt_prize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ""
    context.user_data['prize']=update.message.text
    await update.message.reply_text(
        'some quality description',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
        )
    
    return SUPERMARKT_PRODUCT_QUALITY



async def supermarkt_quality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ""
    context.user_data['supermarkt_extra']=update.message.text
    await update.message.reply_text(
        'thanks! prize succesfully added',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
        )
    
    super_name=context.user_data['supermarket']
    product= context.user_data['product']
    prize= context.user_data['prize']
    extra= context.user_data['supermarkt_extra']
    updateExcel(path=CSV_PATH,sheetName=super_name,sheet_columns=["Producto","Precio","Calidad"],sheet_data=[product,prize,extra])
    return ConversationHandler.END



def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('cost', cost_start)],
        states={
            TOTAL_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, total_cost)],
            COST_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_description)],
            COST_EXTRA_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_extra_desc)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    supermarkt_handler= ConversationHandler(
        entry_points=[CommandHandler('Super',supermarkt_start)],
        states={
            SUPERMARKT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND,supermarkt_name)],
            SUPERMARKT_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND,supermarkt_product)],
            SUPERMARKT_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND,supermarkt_action)],
            SUPERMARKT_PRODUCT_PRIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND,supermarkt_prize)],
            SUPERMARKT_PRODUCT_QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND,supermarkt_quality)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    
    application.add_handler(supermarkt_handler)
    # Handle the case when a user sends /cost but they're not in a conversation
    application.add_handler(CommandHandler('cost', cost_start))

    application.run_polling()


if __name__ == '__main__':
    main()