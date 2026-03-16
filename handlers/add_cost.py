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
        '<b>Ingresa el gasto en el siguiente orden:\n'
        'Costo → Descripción → Info Extra\n'
        'Para cancelar usa /cancel</b>',
        parse_mode='HTML',
    )
    return TOTAL_COST


async def total_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive cost value"""

    try:
        cost = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "❌ Por favor ingresa un número válido para el costo."
        )
        return TOTAL_COST

    context.user_data["total_cost"] = cost

    await update.message.reply_text(
        f"<b>Costo registrado: {cost}\n"
        f"Ahora ingresa la descripción del gasto.</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_DESCRIPTION


async def cost_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive description"""

    context.user_data["cost_description"] = update.message.text

    await update.message.reply_text(
        "<b>Agrega una descripción extra o envía un espacio si no hay.</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_EXTRA_DESC


async def cost_extra_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save expense"""

    context.user_data["cost_extra_desc"] = update.message.text

    try:

        updateExcel(
            path=context.bot_data["CSV_PATH"],
            sheetName="GastosVarios",
            sheet_columns=["Description", "Cuantity", "Extra"],
            sheet_data=[
                context.user_data["total_cost"],
                context.user_data["cost_description"],
                context.user_data["cost_extra_desc"],
            ],
        )

        await update.message.reply_text(
            f"✅ Gasto agregado correctamente\n\n"
            f"💰 Monto: {context.user_data['total_cost']}\n"
            f"📝 Descripción: {context.user_data['cost_description']}\n"
            f"📌 Extra: {context.user_data['cost_extra_desc']}",
            reply_markup=ReplyKeyboardRemove(),
        )

    except Exception as e:

        await update.message.reply_text(
            "❌ Error al guardar el gasto."
        )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""

    await update.message.reply_text(
        "Operación cancelada.",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data.clear()

    return ConversationHandler.END


cost_handler = ConversationHandler(
    entry_points=[CommandHandler("cost", cost_start)],
    states={
        TOTAL_COST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, total_cost)
        ],
        COST_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, cost_description)
        ],
        COST_EXTRA_DESC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, cost_extra_desc)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)