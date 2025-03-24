import json

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
