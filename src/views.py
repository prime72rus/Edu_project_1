import json

from config import PATH_TO_OPERATIONS
from src.utils import (
    api_currency_rates,
    api_currency_stocks,
    calculate_cashback,
    calculate_total_expenses,
    convert_stock_price,
    get_greeting,
    get_top_operations,
    get_unique_card_number,
    read_xlsx,
    selecting_data_by_date,
)


def web_site_main(user_input: str) -> None:
    """
    Функция принимает на вход DataFrame и пользовательскую дату в формате YYYY-MM-DD HH:MM:SS
    и возвращающую JSON-ответ со следующими данными:
    Приветствие в формате — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени.
    По каждой карте: последние 4 цифры карты; общая сумма расходов; кешбэк (1 рубль на каждые 100 рублей).
    Топ-5 транзакций по сумме платежа.
    Курс валют.
    Стоимость акций из S&P500.
    """
    data_df = read_xlsx(PATH_TO_OPERATIONS)
    data = selecting_data_by_date(data_df, user_input)
    greeting = get_greeting()
    if data.empty:
        stock = api_currency_stocks()
        currency_rates = api_currency_rates()
        stocks_price = convert_stock_price(stock)
        response = {
            "greeting": greeting,
            "cards": [],
            "top_transactions": [],
            "currency_rates": currency_rates,
            "stock_prices": stocks_price
        }
    else:
        cards_info = []
        card_list = get_unique_card_number(data)
        for card in card_list:
            total_expenses = calculate_total_expenses(data, card)
            cashback = calculate_cashback(total_expenses)

            card_info = {"last_digits": card[-4:], "total_spent": total_expenses, "cashback": cashback}
            cards_info.append(card_info)

        stock = api_currency_stocks()
        top_operations = get_top_operations(data)
        currency_rates = api_currency_rates()
        stocks_price = convert_stock_price(stock)
        response = {
            "greeting": greeting,
            "cards": cards_info,
            "top_transactions": top_operations,
            "currency_rates": currency_rates,
            "stock_prices": stocks_price
        }
    output_data = json.dumps(response, ensure_ascii=False, indent=4)
    print(output_data)

if __name__ == "__main__":
    web_site_main("2018-01-15 12:00:00")