from unittest.mock import patch
from io import StringIO
import pandas as pd
import json
from src.views import web_site_main


# Тест функции web_site_main
@patch("sys.stdout", new_callable=StringIO)
@patch("src.views.convert_stock_price")
@patch("src.views.api_currency_rates")
@patch("src.views.get_top_operations")
@patch("src.views.api_currency_stocks")
@patch("src.views.calculate_cashback")
@patch("src.views.calculate_total_expenses")
@patch("src.views.get_unique_card_number")
@patch("src.views.get_greeting")
@patch("src.views.selecting_data_by_date")
@patch("src.views.read_xlsx")
def test_web_site_main(
    mock_read_xlsx,
    mock_selecting_data_by_date,
    mock_get_greeting,
    mock_get_unique_card_number,
    mock_calculate_total_expenses,
    mock_calculate_cashback,
    mock_api_currency_stocks,
    mock_get_top_operations,
    mock_api_currency_rates,
    mock_convert_stock_price,
    mock_stdout,
):
    # Мокирование данных
    mock_read_xlsx.__name__ = "read_xlsx"
    mock_selecting_data_by_date.__name__ = "selecting_data_by_date"
    mock_get_greeting.__name__ = "get_greeting"
    mock_get_unique_card_number.__name__ = "get_unique_card_number"
    mock_calculate_total_expenses.__name__ = "calculate_total_expenses"
    mock_calculate_cashback.__name__ = "calculate_cashback"
    mock_api_currency_stocks.__name__ = "api_currency_stocks"
    mock_get_top_operations.__name__ = "get_top_operations"
    mock_api_currency_rates.__name__ = "api_currency_rates"
    mock_convert_stock_price.__name__ = "convert_stock_price"


    mock_read_xlsx.return_value = pd.DataFrame({
        "Дата операции": ["2023-01-01 12:00:00", "2023-01-15 14:00:00"],
        "Номер карты": ["1234567890123456", "1234567890123456"],
        "Сумма платежа": [-1000.0, -500.0],
        "Статус": ["OK", "OK"],
        "Категория": ["Food", "Transport"],
        "Описание": ["Groceries", "Bus ticket"],
        "Дата платежа": ["01.01.2023", "15.01.2023"],
    })

    # Настройка поведения моков
    mock_selecting_data_by_date.return_value = pd.DataFrame({
        "Дата операции": ["2023-01-15 14:00:00"],
        "Номер карты": ["1234567890123456"],
        "Сумма платежа": [-500.0],
        "Статус": ["OK"],
        "Категория": ["Transport"],
        "Описание": ["Bus ticket"],
        "Дата платежа": ["15.01.2023"],
    })
    mock_get_greeting.return_value = "Добрый день"
    mock_get_unique_card_number.return_value = ["1234567890123456"]
    mock_calculate_total_expenses.return_value = 500.0
    mock_calculate_cashback.return_value = 5
    mock_get_top_operations.return_value = [
        {"date": "15.01.2023", "amount": -500.0, "category": "Transport", "description": "Bus ticket"}
    ]
    mock_api_currency_rates.return_value = [{"currency": "USD", "rate": 70.0}]
    mock_api_currency_stocks.return_value = [{"stock": "AAPL", "price": "150.0"}]
    mock_convert_stock_price.return_value = [{"stock": "AAPL", "price": 10500.0}]

    # Вызов тестируемой функции
    web_site_main("2023-01-15 12:00:00")

    # Проверка вывода
    output = mock_stdout.getvalue()
    expected_output = json.dumps({
            "greeting": "Добрый день",
            "cards": [{"last_digits": "3456", "total_spent": 500.0, "cashback": 5}],
            "top_transactions": [
                {"date": "15.01.2023", "amount": -500.0, "category": "Transport", "description": "Bus ticket"}
            ],
            "currency_rates": [{"currency": "USD", "rate": 70.0}],
            "stock_prices": [{"stock": "AAPL", "price": 10500.0}]
        }, ensure_ascii=False, indent=4)


    assert json.loads(output) == json.loads(expected_output)


# Тест функции web_site_main для случая пустых данных
@patch("src.views.read_xlsx")
@patch("src.views.selecting_data_by_date")
@patch("src.views.get_greeting")
@patch("src.views.api_currency_rates")
@patch("src.views.api_currency_stocks")
@patch("src.views.convert_stock_price")
@patch("sys.stdout", new_callable=StringIO)
def test_web_site_main_empty_data(
    mock_stdout,
    mock_convert_stock_price,
    mock_api_currency_stocks,
    mock_api_currency_rates,
    mock_get_greeting,
    mock_selecting_data_by_date,
    mock_read_xlsx,
):
    # Мокирование данных
    mock_read_xlsx.__name__ = "read_xlsx"
    mock_selecting_data_by_date.__name__ = "selecting_data_by_date"
    mock_get_greeting.__name__ = "get_greeting"
    mock_api_currency_stocks.__name__ = "api_currency_stocks"
    mock_api_currency_rates.__name__ = "api_currency_rates"
    mock_convert_stock_price.__name__ = "convert_stock_price"

    mock_read_xlsx.return_value = pd.DataFrame({
        "Дата операции": ["01.01.2023 12:00:00", "15.01.2023 14:00:00"],
        "Номер карты": ["1234567890123456", "1234567890123456"],
        "Сумма платежа": [-1000.0, -500.0],
        "Статус": ["OK", "OK"],
        "Категория": ["Food", "Transport"],
        "Описание": ["Groceries", "Bus ticket"],
        "Дата платежа": ["01.01.2023 12:00:00", "15.01.2023 14:00:00"],
    })

    # Настройка поведения моков
    mock_selecting_data_by_date.return_value = pd.DataFrame()  # Пустой DataFrame
    mock_get_greeting.return_value = "Доброе утро"
    mock_api_currency_rates.return_value = [{"currency": "USD", "rate": 84.83}, {"currency": "EUR", "rate": 91.85}]
    mock_api_currency_stocks.return_value = [{"stock": "AAPL", "price": "150.0"}]
    mock_convert_stock_price.return_value = [{"stock": "AAPL", "price": 12724.5}]

    # Вызов тестируемой функции
    web_site_main("2023-01-15 12:00:00")

    # Проверка вывода
    output = mock_stdout.getvalue()
    expected_output = json.dumps({
        "greeting": "Доброе утро",
        "cards": [],
        "top_transactions": [],
        "currency_rates": [{"currency": "USD", "rate": 84.83}, {"currency": "EUR", "rate": 91.85}],
        "stock_prices": [{"stock": "AAPL", "price": 12724.5}]
    }, ensure_ascii=False, indent=4)

    assert json.loads(output) == json.loads(expected_output)