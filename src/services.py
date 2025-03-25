import json
import logging

from config import PATH_TO_LOGGER, PATH_TO_OPERATIONS
from src.utils import read_xlsx

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"{PATH_TO_LOGGER}/services.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def search_translations() -> None:
    """
    Функция поиска операций по переводу физическим лицам.
    """
    operation_df = read_xlsx(PATH_TO_OPERATIONS)
    logger.info(f"{search_translations.__name__} Получены данные из файла {PATH_TO_OPERATIONS}")
    pattern = r"^\S+ \S\.$"
    filter_data = operation_df[
        (operation_df["Категория"] == "Переводы") & (operation_df["Описание"].str.contains(pattern, na=False))
    ]
    filter_data_dict = filter_data.to_dict(orient="records")
    logger.info(f"{search_translations.__name__} Вывод данных в консоль")
    print(json.dumps(filter_data_dict, ensure_ascii=False, indent=4))
