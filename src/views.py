import json
import logging

from config import PATH_TO_LOGGER, PATH_TO_OPERATIONS
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
    selecting_data_by_date
)

logger = logging.getLogger("views")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"{PATH_TO_LOGGER}/views.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


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
    logger.info(f"{web_site_main.__name__} Вызов функции {read_xlsx.__name__}")
    data_df = read_xlsx(PATH_TO_OPERATIONS)
    logger.info(f"{web_site_main.__name__} Вызов функции {selecting_data_by_date.__name__}")
    data = selecting_data_by_date(data_df, user_input)
    logger.info(f"{web_site_main.__name__} Вызов функции {get_greeting.__name__}")
    greeting = get_greeting()
    if data.empty:
        logger.info(f"{web_site_main.__name__} Вызов функции {api_currency_stocks.__name__}")
        stock = api_currency_stocks()
        logger.info(f"{web_site_main.__name__} Вызов функции {api_currency_rates.__name__}")
        currency_rates = api_currency_rates()
        logger.info(f"{web_site_main.__name__} Вызов функции {convert_stock_price.__name__}")
        stocks_price = convert_stock_price(stock)
        response = {
            "greeting": greeting,
            "cards": [],
            "top_transactions": [],
            "currency_rates": currency_rates,
            "stock_prices": stocks_price,
        }
    else:
        cards_info = []
        logger.info(f"{web_site_main.__name__} Вызов функции {get_unique_card_number.__name__}")
        card_list = get_unique_card_number(data)
        for card in card_list:
            logger.info(f"{web_site_main.__name__} Вызов функции {calculate_total_expenses.__name__}")
            total_expenses = calculate_total_expenses(data, card)
            logger.info(f"{web_site_main.__name__} Вызов функции {calculate_cashback.__name__}")
            cashback = calculate_cashback(total_expenses)

            card_info = {"last_digits": card[-4:], "total_spent": total_expenses, "cashback": cashback}
            cards_info.append(card_info)
        logger.info(f"{web_site_main.__name__} Вызов функции {api_currency_stocks.__name__}")
        stock = api_currency_stocks()
        logger.info(f"{web_site_main.__name__} Вызов функции {get_top_operations.__name__}")
        top_operations = get_top_operations(data)
        logger.info(f"{web_site_main.__name__} Вызов функции {api_currency_rates.__name__}")
        currency_rates = api_currency_rates()
        logger.info(f"{web_site_main.__name__} Вызов функции {convert_stock_price.__name__}")
        stocks_price = convert_stock_price(stock)
        response = {
            "greeting": greeting,
            "cards": cards_info,
            "top_transactions": top_operations,
            "currency_rates": currency_rates,
            "stock_prices": stocks_price,
        }
    output_data = json.dumps(response, ensure_ascii=False, indent=4)
    logger.info(f"{web_site_main.__name__} Вывод данных в консоль")
    print(output_data)
