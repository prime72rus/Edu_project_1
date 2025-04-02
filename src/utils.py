import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_TO_LOGGER, PATH_TO_OPERATIONS, PATH_TO_USER_SETTINGS

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"{PATH_TO_LOGGER}/utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def read_xlsx(xlsx_file_path: Path) -> pd.DataFrame:
    """
    Функция для считывания финансовых операций из XLSX-файла. Принимает путь к файлу XLSX в качестве аргумента
    и возвращает DataFrame с банковскими операциями.
    """
    transactions_df = pd.read_excel(xlsx_file_path)
    logger.info(f"{read_xlsx.__name__} Чтение данных из файла {PATH_TO_OPERATIONS}")

    return transactions_df


def checking_date_from_user(user_input_date: str) -> str:
    """
    Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    проверяет ее на соответствие шаблону ввода, в случае совпадения возвращает строку в формате YYYY-MM-DD HH:MM:SS.
    """
    datetime.strptime(user_input_date, "%Y-%m-%d %H:%M:%S")
    logger.info(f"{checking_date_from_user.__name__} Проверка ввода от пользователя")
    return user_input_date


def selecting_data_by_date(data_for_selection: pd.DataFrame, user_input_datetime: str) -> pd.DataFrame:
    """
    Функция принимает на вход DataFrame и пользовательскую дату в формате YYYY-MM-DD HH:MM:SS,
    осуществляет выборку - это данные с начала месяца, на который выпадает входящая дата, по входящую дату.
    """
    data_for_selection["Дата операции"] = pd.to_datetime(
        data_for_selection["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )

    user_datetime = pd.to_datetime(user_input_datetime, format="%Y-%m-%d %H:%M:%S")

    start_of_month = user_datetime.replace(day=1, hour=0, minute=0, second=0)

    filtered_data = data_for_selection[
        (data_for_selection["Дата операции"] >= start_of_month)
        & (data_for_selection["Дата операции"] <= user_datetime)
        & (data_for_selection["Статус"] == "OK")
    ]
    logger.info(f"{selecting_data_by_date.__name__} Фильтрация данных по дате")
    return filtered_data


def get_greeting() -> str:
    """
    Функция возвращает строку приветствия в зависимости от текущего времени суток.
    """
    logger.info(f"{get_greeting.__name__} Выбор приветствия")
    current_time = datetime.now().time()
    hour = current_time.hour
    minute = current_time.minute

    # Утро: 6:00 - 11:59
    if (hour == 6 and minute >= 0) or (7 <= hour < 12):
        return "Доброе утро"
    # День: 12:00 - 17:59
    elif (hour == 12 and minute >= 0) or (13 <= hour < 18):
        return "Добрый день"
    # Вечер: 18:00 - 22:59
    elif (hour == 18 and minute >= 0) or (19 <= hour < 23):
        return "Добрый вечер"
    # Ночь: 23:00 - 5:59
    else:
        return "Доброй ночи"


def get_unique_card_number(data_df: pd.DataFrame) -> list:
    """
    Функция получения уникальных номеров карт.
    """
    unique_cards = list(data_df["Номер карты"].dropna().unique())
    logger.info(f"{get_unique_card_number.__name__} Получен список номеров банковских карт")
    return unique_cards


def calculate_total_expenses(data_df: pd.DataFrame, card_number: str) -> float:
    """
    Функция для расчета суммы операций по платежам каждой карты.
    """
    card_data = data_df[data_df["Номер карты"] == card_number]
    total_expenses_calc = float(round(abs(card_data[card_data["Сумма платежа"] < 0]["Сумма платежа"].sum()), 2))
    logger.info(f"{calculate_total_expenses.__name__} Расчет суммы операций по платежам")
    return total_expenses_calc


def calculate_cashback(input_total_expenses: float) -> int:
    """
    Функция для расчета кешбэк (1 рубль на каждые 100 рублей)
    """
    logger.info(f"{calculate_cashback.__name__} Посчитан кешбэк")
    return int(input_total_expenses // 100)


def get_top_operations(data_df: pd.DataFrame) -> list[dict]:
    """
    Функция для получения топ-5 транзакций по сумме платежа
    """
    operations_data = data_df.nlargest(5, "Сумма платежа")[["Дата платежа", "Сумма платежа", "Категория", "Описание"]]

    operations = operations_data.to_dict(orient="records")
    top_operations = []
    for operation in operations:
        operations_rename_key = {
            "date": operation["Дата платежа"],
            "amount": operation["Сумма платежа"],
            "category": operation["Категория"],
            "description": operation["Описание"],
        }
        top_operations.append(operations_rename_key)
    logger.info(f"{get_top_operations.__name__} Получен список топ-5 по сумме операций")
    return top_operations


def get_settings_from_file() -> dict:
    """
    Функция получения пользовательских настроек из файла user_settings.json
    """

    with open(PATH_TO_USER_SETTINGS, encoding="utf-8") as file_json:
        data_from_file = dict(json.load(file_json))
        logger.info(f"{get_settings_from_file.__name__} Получены данные пользовательских настроек из файла")
        return data_from_file


def api_currency_rates() -> list[dict]:
    """
    Функция получения курса валют из внешнего API
    """
    result = []
    currency_list = get_settings_from_file()["user_currencies"]
    load_dotenv()
    api_key = os.getenv("API_KEY_RATES")
    url = "https://api.apilayer.com/exchangerates_data/latest"
    for base in currency_list:
        payload = {"symbols": "RUB", "base": base}
        headers = {"apikey": api_key}

        response = requests.get(url, headers=headers, params=payload)
        # status_code = response.status_code
        currency_rate = json.loads(response.text)
        rates = currency_rate.get("rates")
        result.append({"currency": base, "rate": round(rates["RUB"], 2)})
    logger.info(f"{api_currency_rates.__name__} Получены данные курса валют из внешнего API")
    return result


def api_convert_currency() -> float:
    """
    Функция получения курса USD из внешнего API для конвертации стоимости акций
    """
    load_dotenv()
    api_key = os.getenv("API_KEY_RATES")
    url = "https://api.apilayer.com/exchangerates_data/latest"
    payload = {"symbols": "RUB", "base": "USD"}
    headers = {"apikey": api_key}

    response = requests.get(url, headers=headers, params=payload)
    # status_code = response.status_code
    currency_rate = json.loads(response.text)
    rates = currency_rate.get("rates")
    usd_rate = round(rates["RUB"], 2)
    logger.info(f"{api_convert_currency.__name__} Получен курс USD для конвертации стоимости акций")
    return float(usd_rate)


def api_currency_stocks() -> list[dict]:
    """
    Функция получения стоимости акций из внешнего API
    """
    result = []
    currency_list = get_settings_from_file()["user_stocks"]
    load_dotenv()
    api_key = os.getenv("API_KEY_STOCKS")

    for stock in currency_list:
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=compact&"
            f"symbol={stock}&apikey={api_key}"
        )

        response = requests.get(url)
        # status_code = response.status_code
        stocks = json.loads(response.text)
        stock_data = stocks["Meta Data"]["3. Last Refreshed"]
        stock_price = stocks["Time Series (Daily)"][stock_data]["4. close"]
        result.append({"stock": stock, "price": stock_price})
        logger.info(f"{api_currency_stocks.__name__} Получена стоимость акций")
    return result


def convert_stock_price(stock_price: list[dict]) -> list[dict]:
    """
    Функция конвертации стоимости акций из USD в рубли
    """
    usd_rate = api_convert_currency()
    for value in stock_price:
        value["price"] = round(usd_rate * float(value["price"]), 2)
        logger.info(f"{convert_stock_price.__name__} Конвертация стоимости акций из USD в RUB")
    return stock_price
