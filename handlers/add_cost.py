from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from states import TOTAL_COST, COST_DESCRIPTION, COST_EXTRA_DESC
from interfaces.excel_driver import (
    update_excel,
    get_last_expenses,
    get_monthly_total,
    delete_last_expense,
    get_expenses_for_month,
    get_monthly_category_breakdown,
)


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

    extra_options_keyboard = ReplyKeyboardMarkup(
        [["comida", "supermercado"], ["tecnologia", "entretenimiento"], ["otro"]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "<b>Add extra details. You can choose one option or write your own text.</b>",
        parse_mode="HTML",
        reply_markup=extra_options_keyboard,
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
                    [['/cost', '/market'], ['/latest', '/total'], ['/lastmonth', '/analysis'], ['/delete', '/help']],
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


import datetime as _dt


async def show_monthly_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return total expenses for the current month or a given month number."""
    month = _dt.date.today().month
    if context.args:
        try:
            month = int(context.args[0])
            if not 1 <= month <= 12:
                await update.message.reply_text("Please enter a valid month number (1-12).")
                return
        except ValueError:
            await update.message.reply_text("Please enter a valid month number (1-12).")
            return

    total = get_monthly_total(path=context.bot_data["CSV_PATH"], month=month)
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    await update.message.reply_text(
        f"<b>Total for {month_names[month - 1]}: \u20ac{total:.2f}</b>",
        parse_mode="HTML",
    )


def _get_previous_month_date():
    today = _dt.date.today()
    first_day_current_month = today.replace(day=1)
    return first_day_current_month - _dt.timedelta(days=1)


async def show_last_month_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return all expenses for the previous month."""
    last_month_date = _get_previous_month_date()
    expenses = get_expenses_for_month(
        path=context.bot_data["CSV_PATH"],
        year=last_month_date.year,
        month=last_month_date.month,
    )

    if not expenses:
        await update.message.reply_text("No expenses found for last month.")
        return

    month_label = last_month_date.strftime("%B %Y")
    lines = [f"<b>Expenses for {month_label}:</b>\n"]
    for i, exp in enumerate(expenses, start=1):
        date = exp.get("Date", "")
        if hasattr(date, "date"):
            date = date.date()
        desc = exp.get("Description", "")
        extra = exp.get("Extra", "")
        amount = exp.get("Amount", exp.get("Cuantity", ""))
        suffix = f" ({extra})" if extra else ""
        lines.append(f"{i}. {date} | €{amount} | {desc}{suffix}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def show_spending_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show spending analysis by category for the previous month."""
    last_month_date = _get_previous_month_date()
    breakdown = get_monthly_category_breakdown(
        path=context.bot_data["CSV_PATH"],
        year=last_month_date.year,
        month=last_month_date.month,
    )

    if not breakdown:
        await update.message.reply_text("No data available to analyze last month.")
        return

    month_label = last_month_date.strftime("%B %Y")
    total = sum(amount for _, amount in breakdown)
    top_category, top_amount = breakdown[0]
    lines = [
        f"<b>Spending analysis for {month_label}:</b>",
        f"Top category: <b>{top_category}</b> (€{top_amount:.2f})",
        f"Monthly total: €{total:.2f}",
        "",
        "<b>Category breakdown:</b>",
    ]
    for category, amount in breakdown:
        lines.append(f"- {category}: €{amount:.2f}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def delete_last_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete the last registered expense."""
    deleted = delete_last_expense(path=context.bot_data["CSV_PATH"])
    if deleted is None:
        await update.message.reply_text("No expenses to delete.")
        return

    date = deleted.get("Date", "")
    if hasattr(date, "date"):
        date = date.date()
    desc = deleted.get("Description", "")
    amount = deleted.get("Amount", deleted.get("Cuantity", ""))
    await update.message.reply_text(
        f"Last expense deleted:\n{date} | \u20ac{amount} | {desc}"
    )


async def show_last_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return the last N expenses added (default 6)"""

    n = 5
    if context.args:
        try:
            n = int(context.args[0])
            if n <= 0:
                await update.message.reply_text("Please enter a positive number.")
                return
        except ValueError:
            await update.message.reply_text("Please enter a valid number.")
            return

    expenses = get_last_expenses(path=context.bot_data["CSV_PATH"], n=n)

    if not expenses:
        await update.message.reply_text("No expenses have been registered yet.")
        return

    lines = [f"<b>Last {n} expenses:</b>\n"]
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
