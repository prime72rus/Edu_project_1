from unittest.mock import patch
from io import StringIO
import pandas as pd
import json

from src.services import search_translations


@patch("sys.stdout", new_callable=StringIO)
@patch("src.services.read_xlsx")
def test_search_translations(mock_read_xlsx, mock_stdout):
    mock_read_xlsx.__name__ = "read_xlsx"
    mock_read_xlsx.return_value = pd.DataFrame({
          "Дата операции": ["31.12.2021 00:12:53", "30.12.2021 22:22:03"],
          "Дата платежа": ["31.12.2021", "31.12.2021"],
          "Статус": ["OK", "OK"],
          "Сумма операции": [-800.0, -20000.0],
          "Валюта операции": ["RUB", "RUB"],
          "Сумма платежа": [-800.0, -20000.0],
          "Валюта платежа": ["RUB", "RUB"],
          "Категория": ["Переводы", "Переводы"],
          "Описание": ["Перевод организации", "Константин Л."],
          "Бонусы (включая кэшбэк)": [0, 0],
          "Округление на инвесткопилку": [0, 0],
          "Сумма операции с округлением": [800.0, 20000.0]
    })

    search_translations()

    output = mock_stdout.getvalue()
    expected_output = json.dumps([{
                "Дата операции": "30.12.2021 22:22:03",
                "Дата платежа": "31.12.2021",
                "Статус": "OK",
                "Сумма операции": -20000.0,
                "Валюта операции": "RUB",
                "Сумма платежа": -20000.0,
                "Валюта платежа": "RUB",
                "Категория": "Переводы",
                "Описание": "Константин Л.",
                "Бонусы (включая кэшбэк)": 0,
                "Округление на инвесткопилку": 0,
                "Сумма операции с округлением": 20000.0
            }], ensure_ascii=False, indent=4)

    assert json.loads(output) == json.loads(expected_output)
