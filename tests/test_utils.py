import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time
from pandas import DataFrame

from src.utils import (
    api_convert_currency,
    api_currency_rates,
    api_currency_stocks,
    calculate_cashback,
    calculate_total_expenses,
    checking_date_from_user,
    convert_stock_price,
    get_greeting,
    get_top_operations,
    get_unique_card_number,
    read_xlsx,
    selecting_data_by_date
)


def test_read_xlsx(mock_xlsx_data, tmp_path):
    file_path = tmp_path / "test.xlsx"
    mock_xlsx_data.to_excel(file_path, index=False)

    result = read_xlsx(file_path)
    assert isinstance(result, DataFrame)
    assert len(result) == 2
    assert list(result.columns) == list(mock_xlsx_data.columns)


@patch("pandas.read_excel")
def test_read_xlsx_exception(mock_read_excel):
    mock_read_excel.side_effect = Exception("Ошибка чтения файла")
    with pytest.raises(Exception, match="Ошибка чтения файла"):
        read_xlsx(Path("nonexistent_file.xlsx"))


@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("2023-01-15 12:30:45", "2023-01-15 12:30:45"),
        ("2023-12-31 23:59:59", "2023-12-31 23:59:59"),
    ],
)
def test_checking_date_from_user_valid(input_date, expected):
    result = checking_date_from_user(input_date)
    assert result == expected


@pytest.mark.parametrize(
    "input_date",
    [
        "2023-01-15 25:30:45",
        "2023-02-30 12:30:45",
        "invalid-date",
    ],
)
def test_checking_date_from_user_invalid(input_date):
    with pytest.raises(ValueError):
        checking_date_from_user(input_date)


def test_selecting_data_by_date(mock_xlsx_data):
    user_input_datetime = "2023-01-15 14:30:00"
    result = selecting_data_by_date(mock_xlsx_data, user_input_datetime)
    assert len(result) == 2
    assert result.iloc[1]["Сумма платежа"] == -200


@freeze_time("2023-11-20 06:00:00")
def test_get_greeting():
    with freeze_time("2023-11-20 06:00:00"):
        assert get_greeting() == "Доброе утро"
    with freeze_time("2023-11-20 12:00:00"):
        assert get_greeting() == "Добрый день"
    with freeze_time("2023-11-20 18:00:00"):
        assert get_greeting() == "Добрый вечер"
    with freeze_time("2023-11-20 23:00:00"):
        assert get_greeting() == "Доброй ночи"


@patch("requests.get")
def test_api_currency_rates(mock_get, mock_settings_file):
    mock_response = MagicMock()
    mock_response.text = '{"rates": {"RUB": 75.0}}'
    mock_get.return_value = mock_response

    with patch("config.PATH_TO_USER_SETTINGS", mock_settings_file):
        result = api_currency_rates()

    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 75.0


@patch("requests.get")
@patch("os.getenv")
def test_api_convert_currency(mock_getenv, mock_requests_get):
    mock_getenv.return_value = "mock_api_key_rates"

    mock_response = MagicMock()
    mock_response.text = '{"rates": {"RUB": 75.1234}}'
    mock_requests_get.return_value = mock_response

    result = api_convert_currency()

    assert result == 75.12

    mock_getenv.assert_called_once_with("API_KEY_RATES")

    mock_requests_get.assert_called_once_with(
        "https://api.apilayer.com/exchangerates_data/latest",
        headers={"apikey": "mock_api_key_rates"},
        params={"symbols": "RUB", "base": "USD"}
    )


@patch("requests.get")
@patch("os.getenv")
def test_api_convert_currency_missing_rate(mock_getenv, mock_requests_get):
    mock_getenv.return_value = "mock_api_key_rates"

    mock_response = MagicMock()
    mock_response.text = '{"rates": {}}'
    mock_requests_get.return_value = mock_response

    with pytest.raises(KeyError):
        api_convert_currency()


@patch("requests.get")
@patch("os.getenv")
def test_api_convert_currency_invalid_json(mock_getenv, mock_requests_get):
    mock_getenv.return_value = "mock_api_key_rates"

    mock_response = MagicMock()
    mock_response.text = "invalid_json"
    mock_requests_get.return_value = mock_response

    with pytest.raises(json.JSONDecodeError):
        api_convert_currency()


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "Номер карты": ["1234567890", "0987654321", "1234567890", None],
            },
            ["1234567890", "0987654321"],
        ),
        (
            {
                "Номер карты": [None, None, None],
            },
            [],
        ),
        (
            {
                "Номер карты": [],
            },
            [],
        ),
        (
            {
                "Номер карты": ["1111111111", "1111111111", None],
            },
            ["1111111111"],
        ),
    ],
)
def test_get_unique_card_number(input_data, expected):
    data_df = DataFrame(input_data)

    result = get_unique_card_number(data_df)

    assert result == expected


@pytest.mark.parametrize(
    "input_data, card_number, expected",
    [
        (
            {
                "Номер карты": ["1234567890", "1234567890", "0987654321"],
                "Сумма платежа": [-100.50, -200.25, -50.0],
            },
            "1234567890",
            300.75,
        ),
        (
            {
                "Номер карты": ["1234567890", "1234567890", "0987654321"],
                "Сумма платежа": [100.0, 200.0, 50.0],
            },
            "1234567890",
            0.0,
        ),
        (
            {
                "Номер карты": ["0987654321", "0987654321"],
                "Сумма платежа": [-100.0, -200.0],
            },
            "1234567890",
            0.0,
        ),
        (
            {
                "Номер карты": [],
                "Сумма платежа": [],
            },
            "1234567890",
            0.0,
        ),
        (
            {
                "Номер карты": ["1234567890", "1234567890", "1234567890"],
                "Сумма платежа": [-100.0, 200.0, -50.0],
            },
            "1234567890",
            150.0,
        ),
    ],
)
def test_calculate_total_expenses(input_data, card_number, expected):
    data_df = DataFrame(input_data)

    result = calculate_total_expenses(data_df, card_number)

    assert result == expected


@pytest.mark.parametrize(
    "input_total_expenses, expected",
    [
        (300.0, 3),
        (350.0, 3),
        (100.0, 1),
        (99.99, 0),
        (0.0, 0),
        (123456.78, 1234)
    ]
)
def test_calculate_cashback(input_total_expenses, expected):
    result = calculate_cashback(input_total_expenses)

    assert result == expected


@pytest.mark.parametrize(
    "input_data, expected",
    [
        (
            {
                "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06"],
                "Сумма платежа": [500, 400, 300, 200, 100, 50],
                "Категория": ["A", "B", "C", "D", "E", "F"],
                "Описание": ["Desc1", "Desc2", "Desc3", "Desc4", "Desc5", "Desc6"],
            },
            [
                {"date": "2023-01-01", "amount": 500, "category": "A", "description": "Desc1"},
                {"date": "2023-01-02", "amount": 400, "category": "B", "description": "Desc2"},
                {"date": "2023-01-03", "amount": 300, "category": "C", "description": "Desc3"},
                {"date": "2023-01-04", "amount": 200, "category": "D", "description": "Desc4"},
                {"date": "2023-01-05", "amount": 100, "category": "E", "description": "Desc5"},
            ],
        ),
        (
            {
                "Дата платежа": ["2023-01-01", "2023-01-02"],
                "Сумма платежа": [500, 400],
                "Категория": ["A", "B"],
                "Описание": ["Desc1", "Desc2"],
            },
            [
                {"date": "2023-01-01", "amount": 500, "category": "A", "description": "Desc1"},
                {"date": "2023-01-02", "amount": 400, "category": "B", "description": "Desc2"},
            ],
        ),
        (
            {
                "Дата платежа": [],
                "Сумма платежа": [],
                "Категория": [],
                "Описание": [],
            },
            [],
        ),
        (
            {
                "Дата платежа": ["2023-01-01", "2023-01-02"],
                "Сумма платежа": [0, 0],
                "Категория": ["A", "B"],
                "Описание": ["Desc1", "Desc2"],
            },
            [
                {"date": "2023-01-01", "amount": 0, "category": "A", "description": "Desc1"},
                {"date": "2023-01-02", "amount": 0, "category": "B", "description": "Desc2"},
            ],
        ),
    ],
)
def test_get_top_operations(input_data, expected):
    data_df = DataFrame(input_data)

    result = get_top_operations(data_df)

    assert result == expected


@patch("requests.get")
@patch("os.getenv")
@patch("src.utils.get_settings_from_file")
def test_api_currency_stocks(mock_get_settings, mock_getenv, mock_requests_get, mock_settings_file):
    mock_get_settings.return_value = {"user_stocks": ["AAPL", "GOOGL"]}

    mock_getenv.return_value = "mock_api_key_stocks"

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "Meta Data": {"3. Last Refreshed": "2023-10-01"},
        "Time Series (Daily)": {
            "2023-10-01": {"4. close": "150.00"}
        }
    })
    mock_requests_get.return_value = mock_response

    result = api_currency_stocks()

    assert len(result) == 2
    assert result[0] == {"stock": "AAPL", "price": "150.00"}
    assert result[1] == {"stock": "GOOGL", "price": "150.00"}

    mock_requests_get.assert_any_call(
        "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=compact&"
        "symbol=AAPL&apikey=mock_api_key_stocks"
    )
    mock_requests_get.assert_any_call(
        "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=compact&"
        "symbol=GOOGL&apikey=mock_api_key_stocks"
    )


@patch("requests.get")
@patch("os.getenv")
@patch("src.utils.get_settings_from_file")
def test_api_currency_stocks_empty_stocks(mock_get_settings, mock_getenv, mock_requests_get):
    mock_get_settings.return_value = {"user_stocks": []}

    result = api_currency_stocks()

    assert result == []

    mock_requests_get.assert_not_called()


@pytest.mark.parametrize(
    "input_data, mock_usd_rate, expected",
    [
        (
            [{"stock": "AAPL", "price": "150.00"}, {"stock": "GOOGL", "price": "2500.00"}],
            75.0,
            [{"stock": "AAPL", "price": 11250.0}, {"stock": "GOOGL", "price": 187500.0}],
        ),
        (
            [],
            75.0,
            [],
        ),
        (
            [{"stock": "AAPL", "price": "0.00"}],
            75.0,
            [{"stock": "AAPL", "price": 0.0}],
        ),
        (
            [{"stock": "AAPL", "price": "123.45"}, {"stock": "GOOGL", "price": "678.90"}],
            75.0,
            [{"stock": "AAPL", "price": 9258.75}, {"stock": "GOOGL", "price": 50917.5}],
        ),
        (
            [{"stock": "AAPL", "price": "-100.00"}],
            75.0,
            [{"stock": "AAPL", "price": -7500.0}],
        ),
    ],
)
@patch("src.utils.api_convert_currency")
def test_convert_stock_price(mock_api_convert_currency, input_data, mock_usd_rate, expected):
    mock_api_convert_currency.return_value = mock_usd_rate

    result = convert_stock_price(input_data)

    assert result == expected

    mock_api_convert_currency.assert_called_once()
