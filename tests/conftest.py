import json
import logging

import pandas as pd
import pytest

disable_loggers = ["utils", "views", "services", "reports", "main"]

def pytest_configure():
    for logger_name in disable_loggers:
        logger = logging.getLogger(logger_name)
        logger.disabled = True

@pytest.fixture
def mock_xlsx_data():
    """Фикстура для создания мок-данных DataFrame."""
    data = {
        "Дата операции": ["01.01.2023 12:00:00", "15.01.2023 14:30:00"],
        "Статус": ["OK", "OK"],
        "Номер карты": ["1234567890", "0987654321"],
        "Сумма платежа": [-100, -200],
        "Категория": ["Развлечения", "Еда"],
        "Описание": ["Кино", "Ужин"],
        "Дата платежа": ["01.01.2023 12:00:00", "15.01.2023 14:30:00"],
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_settings_file(tmp_path):
    """Фикстура для создания временного файла user_settings.json."""
    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "GOOGL"],
    }
    file_path = tmp_path / "user_settings.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(settings, f)
    return file_path

@pytest.fixture
def mock_env(monkeypatch):
    """Фикстура для мокирования переменных окружения."""
    monkeypatch.setenv("API_KEY_RATES", "mock_api_key_rates")
    monkeypatch.setenv("API_KEY_STOCKS", "mock_api_key_stocks")