from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from states import TOTAL_COST, COST_DESCRIPTION, COST_EXTRA_DESC
from interfaces.drvExcel import updateExcel


async def cost_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        '<b>ingresa la plata que gastaste en el siguiente orden:\n'
        'Costo - Descripcion - Info Extra\n'
        'para cancelar ingresa \\cancel</b>',
        parse_mode='HTML',
    )
    return TOTAL_COST


async def total_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['total_cost'] = update.message.text

    await update.message.reply_text(
        f'<b>You entered {update.message.text}.\n'
        f'What is the expense description? </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_DESCRIPTION


async def cost_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['cost_description'] = update.message.text

    await update.message.reply_text(
        f'<b>You entered {update.message.text}.\n'
        f'please enter an extra description or empty space </b>',
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_EXTRA_DESC


async def cost_extra_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['cost_extra_desc'] = update.message.text

    updateExcel(
        path=context.bot_data["CSV_PATH"],
        sheet_columns=["Description", "Cuantity", "Extra"],
        sheet_data=[
            context.user_data['total_cost'],
            context.user_data['cost_description'],
            context.user_data['cost_extra_desc'],
        ],
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


cost_handler = ConversationHandler(
    entry_points=[CommandHandler("cost", cost_start)],
    states={
        TOTAL_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, total_cost)],
        COST_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_description)],
        COST_EXTRA_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost_extra_desc)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)