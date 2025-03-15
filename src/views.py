import json

from config import PATH_TO_OPERATIONS
from src.utils import (
    calculate_cashback,
    calculate_total_expenses,
    checking_date_from_user,
    get_greeting,
    get_top_operations,
    get_unique_card_number,
    read_xlsx,
    selecting_data_by_date,
)


def main() -> None:
    """
    Функция запуска страницы "Главная"
    """
    data = selecting_data_by_date(read_xlsx(PATH_TO_OPERATIONS), checking_date_from_user("2021-08-12 12:03:55"))

    cards_info = []
    for card in get_unique_card_number(data):
        total_expenses = calculate_total_expenses(data, card)
        cashback = calculate_cashback(total_expenses)

        card_info = {"last_digits": card[-4:], "total_spent": total_expenses, "cashback": cashback}
        cards_info.append(card_info)

    response = {"greeting": get_greeting(), "cards": cards_info, "top_transactions": get_top_operations(data)}
    with open("../data/output_data.json", "w", encoding="utf-8") as file_json:
        json.dump(response, file_json, ensure_ascii=False, indent=4)  # type: ignore


if __name__ == "__main__":  # pragma: no cover
    main()
