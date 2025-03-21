import json
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_TO_OPERATIONS, PATH_TO_USER_SETTINGS


def read_xlsx(xlsx_file_path: Path) -> pd.DataFrame:
    """
    Функция для считывания финансовых операций из XLSX-файла. Принимает путь к файлу XLSX в качестве аргумента
    и возвращает DataFrame с банковскими операциями.
    """
    transactions_df = pd.read_excel(xlsx_file_path)
    return transactions_df


def checking_date_from_user(user_input_date: str) -> str:
    """
    Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS,
    проверяет ее на соответствие шаблону ввода, в случае совпадения возвращает строку в формате YYYY-MM-DD HH:MM:SS,
    при несовпадении вызывает исключение.
    """
    pattern = re.compile(
        r"^\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01]) (00|[0-9]|1[0-9]|2[0-3]):([0-9]|[0-5][0-9]):([0-9]|[0-5][0-9])$"
    )
    result_match = pattern.fullmatch(user_input_date)
    if result_match is None:
        raise ValueError("Ввод данных не соответствует формату")
    else:
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

    if filtered_data.empty:
        raise ValueError("Данные за указанный период отсутствуют.")

    return filtered_data


def get_greeting() -> str:
    """
    Функция возвращает строку приветствия в зависимости от текущего времени суток.
    """
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
    Функция получения уникальных номеров карт
    """
    unique_cards = list(data_df["Номер карты"].dropna().unique())
    return unique_cards


def calculate_total_expenses(data_df: pd.DataFrame, card_number: str) -> float:
    card_data = data_df[data_df["Номер карты"] == card_number]
    total_expenses_calc = card_data[card_data["Сумма платежа"] < 0]["Сумма платежа"].sum()
    return float(round(abs(total_expenses_calc), 2))


def calculate_cashback(input_total_expenses: float) -> int:
    """
    Функция для расчета кешбэка (1 рубль на каждые 100 рублей)
    """
    return int(input_total_expenses // 100)


def get_top_operations(data_df: pd.DataFrame) -> list[dict]:
    """
    Функция для получения топ-5 транзакций по сумме платежа
    """
    operations = data_df.nlargest(5, "Сумма платежа")[
        ["Дата платежа", "Сумма платежа", "Категория", "Описание"]
    ].to_dict(orient="records")
    top_operations = []
    for operation in operations:
        operations_rename_key = {
            "date": operation["Дата платежа"],
            "amount": operation["Сумма платежа"],
            "category": operation["Категория"],
            "description": operation["Описание"],
        }
        top_operations.append(operations_rename_key)

    return top_operations


def get_settings_from_file() -> dict:
    """
    Функция получения пользовательских настроек из файла user_settings.json
    """
    with open(PATH_TO_USER_SETTINGS, encoding="utf-8") as file_json:
        data_from_file = dict(json.load(file_json))
        return data_from_file


def api_currency_rates() -> list[dict]:
    """
    Функция получения курса валют из внешнего источника
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

    return result


def api_currency_stocks() -> list[dict]:
    """
    Функция получения курса валют из внешнего источника
    """
    result = []
    currency_list = get_settings_from_file()["user_stocks"]
    load_dotenv()
    api_key = os.getenv("API_KEY_STOCKS")

    for stock in currency_list:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=compact&symbol={stock}&apikey={api_key}"

        response = requests.get(url)
        # status_code = response.status_code
        stocks = json.loads(response.text)
        stocks_data = stocks["Meta Data"]["3. Last Refreshed"]
        temp_result = stocks["Time Series (Daily)"][stocks_data]["4. close"]

        result.append({"stock": stock, "price": round(float(temp_result), 2)})
    return result


if __name__ == "__main__":  # pragma: no cover

    # data = read_xlsx(PATH_TO_OPERATIONS)
    #
    # cards_info = []
    # for card in get_unique_card_number(data):
    #     total_expenses = calculate_total_expenses(data, card)
    #     cashback = calculate_cashback(total_expenses)
    #
    #     card_info = {"last_digits": card[-4:], "total_spent": total_expenses, "cashback": cashback}
    #     cards_info.append(card_info)
    #
    # response = {"greeting": get_greeting(), "cards": cards_info, "top_transactions": get_top_operations(data)}
    # print(json.dumps(response, ensure_ascii=False, indent=4))
    # result_checking = checking_date_from_user("2025-03-12 12:03:55")
    # print(result_checking)

    # result = get_settings_from_file()
    # currency = get_list_currency(result)
    # print(currency)
    # stocks = get_list_stocks(result)
    # print(stocks)
    # print(api_currency_rates())
    api_currency_stocks()
