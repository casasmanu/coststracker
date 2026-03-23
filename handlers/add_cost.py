from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from states import TOTAL_COST, COST_DESCRIPTION, COST_EXTRA_DESC
from interfaces.excel_driver import update_excel, get_last_expenses


async def start_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        '<b>Enter the expense in this order:\n'
        'Amount → Description → Extra Info\n'
        'Use /cancel to abort</b>',
        parse_mode='HTML',
    )
    return TOTAL_COST


async def receive_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive cost value"""

    try:
        cost = float(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the amount."
        )
        return TOTAL_COST

    context.user_data["total_cost"] = cost

    await update.message.reply_text(
        f"<b>Amount recorded: €{cost}\n"
        f"Now enter the expense description.</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_DESCRIPTION


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive description"""

    context.user_data["cost_description"] = update.message.text

    await update.message.reply_text(
        "<b>Add extra details or send a blank message if none.</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    return COST_EXTRA_DESC


async def save_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save expense"""

    context.user_data["cost_extra_desc"] = update.message.text

    try:
        success = update_excel(
            path=context.bot_data["CSV_PATH"],
            sheet_name="VariableExpenses",
            sheet_columns=["Description", "Amount", "Extra"],
            sheet_data=[
                context.user_data["cost_description"],
                context.user_data["total_cost"],
                context.user_data["cost_extra_desc"],
            ],
        )

        if success:
            await update.message.reply_text(
                f"Expense added successfully\n\n"
                f"Amount: €{context.user_data['total_cost']}\n"
                f"Description: {context.user_data['cost_description']}",
            )

            await update.message.reply_text(
                "Do you want to add another expense? Use /cost again or choose another menu option.",
                reply_markup=ReplyKeyboardMarkup(
                    [['/cost', '/market']],
                    one_time_keyboard=False,
                    resize_keyboard=True
                ),
            )
        else:
            await update.message.reply_text(
                "Error while saving the expense."
            )

    except Exception as e:
        await update.message.reply_text(
            "Error while saving the expense."
        )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation"""

    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )

    context.user_data.clear()

    return ConversationHandler.END


async def show_last_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return the last 5 expenses added"""

    expenses = get_last_expenses(path=context.bot_data["CSV_PATH"], n=5)

    if not expenses:
        await update.message.reply_text("No expenses have been registered yet.")
        return

    lines = ["<b>Last 5 expenses:</b>\n"]
    for i, exp in enumerate(reversed(expenses), start=1):
        date = exp.get("Date", "")
        if hasattr(date, "date"):
            date = date.date()
        desc = exp.get("Description", "")
        amount = exp.get("Amount", exp.get("Cuantity", ""))
        line = f"{i}. {date} | €{amount} | {desc}"
        lines.append(line)

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


cost_handler = ConversationHandler(
    entry_points=[CommandHandler("cost", start_cost)],
    states={
        TOTAL_COST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_amount)
        ],
        COST_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)
        ],
        COST_EXTRA_DESC: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_expense)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)