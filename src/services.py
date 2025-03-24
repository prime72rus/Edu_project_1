import json

import pandas as pd

from config import PATH_TO_OPERATIONS
from src.utils import read_xlsx


def search_translations() -> None:
    """
    Функция поиска операций по переводу физическим лицам.
    """
    operation_df = read_xlsx(PATH_TO_OPERATIONS)
    pattern = r"^\S+ \S\.$"
    filter_data = operation_df[
        (operation_df["Категория"] == "Переводы") & (operation_df["Описание"].str.contains(pattern, na=False))
    ]
    filter_data_dict = filter_data.to_dict(orient="records")
    print(json.dumps(filter_data_dict, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    # search_translations()

    return_value = pd.DataFrame(
            {
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
            }
    )

    print(return_value)

    return_value_1 = pd.DataFrame({
        "Дата операции": ["2023-01-01 12:00:00", "2023-01-15 14:00:00"],
        "Номер карты": ["1234567890123456", "1234567890123456"],
        "Сумма платежа": [-1000.0, -500.0],
        "Статус": ["OK", "OK"],
        "Категория": ["Food", "Transport"],
        "Описание": ["Groceries", "Bus ticket"],
        "Дата платежа": ["01.01.2023", "15.01.2023"],
    })
    print(return_value_1)