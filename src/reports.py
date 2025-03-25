import logging
import os
from datetime import datetime, timedelta
from typing import Callable, Optional, ParamSpec, TypeVar

import pandas as pd

from config import PATH_TO_LOGGER, PATH_TO_OPERATIONS, PATH_TO_REPORTS
from src.utils import read_xlsx

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"{PATH_TO_LOGGER}/reports.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

P = ParamSpec("P")
T = TypeVar("T")


def save_to_file_default(func: Callable[P, pd.DataFrame]) -> Callable[P, pd.DataFrame]:
    """
    Декоратор функции для записи отчета по тратам в файл *.xlsx. Имя файла по умолчанию.
    """

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> pd.DataFrame:
        result = func(*args, **kwargs)
        default_filename = f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        result.to_excel(os.path.join(f"{PATH_TO_REPORTS}", default_filename), index=False)
        logger.info(f"Отчет сохранен в файл: {os.path.join(f"{PATH_TO_REPORTS}", default_filename)}")
        return result

    return wrapper


def save_to_file(filename: str) -> Callable[[Callable[P, pd.DataFrame]], Callable[P, pd.DataFrame]]:
    """
    Декоратор функции для записи отчета по тратам в файл *.xlsx. Имя файла вводится пользователем.
    """

    def decorator(func: Callable[P, pd.DataFrame]) -> Callable[P, pd.DataFrame]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> pd.DataFrame:
            result = func(*args, **kwargs)
            result.to_excel(os.path.join(f"{PATH_TO_REPORTS}", f"{filename}.xlsx"), index=False)
            logging.info(f"Отчет сохранен в файл: {os.path.join(f"{PATH_TO_REPORTS}", f"{filename}.xlsx")}")
            return result

        return wrapper

    return decorator


# Функция для расчета трат по категории
@save_to_file("output_data")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    Если дата не передана, используется текущая дата.
    """
    if date is None:
        end_date = datetime.now()
    else:
        end_date = pd.to_datetime(date, format="%Y-%m-%d")

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    start_date = end_date - timedelta(days=90)

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date.strftime("%Y-%m-%d"))
        & (transactions["Дата операции"] <= end_date.strftime("%Y-%m-%d"))
        & (transactions["Категория"] == category)
    ]
    logger.info(f"{spending_by_category.__name__} Данные по категории отфильтрованы")
    return filtered_transactions[["Дата операции", "Категория", "Сумма платежа"]]


if __name__ == "__main__":
    data_df = read_xlsx(PATH_TO_OPERATIONS)
    data_1 = spending_by_category(data_df, "Каршеринг", "2021-10-30")
