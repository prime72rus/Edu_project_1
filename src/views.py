import json

from config import PATH_TO_OPERATIONS
from src.utils import (
    api_currency_rates,
    api_currency_stocks,
    calculate_cashback,
    calculate_total_expenses,
    checking_date_from_user,
    get_greeting,
    get_top_operations,
    get_unique_card_number,
    read_xlsx,
    selecting_data_by_date, convert_stock_price,
)


def web_site_main() -> None:
    """
    Функция запуска страницы "Главная"
    """
    user_input = ""
    while True:
        try:
            user_input = checking_date_from_user(input("Введите дату для анализа в формате YYYY-MM-DD HH:MM:SS:\n"))
        except ValueError:
            print("Формат ввода не соответствует требованиям!\n")
            continue
        else:
            break

    data = selecting_data_by_date(read_xlsx(PATH_TO_OPERATIONS), user_input)

    cards_info = []
    for card in get_unique_card_number(data):
        total_expenses = calculate_total_expenses(data, card)
        cashback = calculate_cashback(total_expenses)

        card_info = {"last_digits": card[-4:], "total_spent": total_expenses, "cashback": cashback}
        cards_info.append(card_info)

    stock = api_currency_stocks()

    response = {
        "greeting": get_greeting(),
        "cards": cards_info,
        "top_transactions": get_top_operations(data),
        "currency_rates": api_currency_rates(),
        "stock_prices": convert_stock_price(stock),
    }
    with open("../data/output_data.json", "w", encoding="utf-8") as file_json:
        json.dump(response, file_json, ensure_ascii=False, indent=4)  # type: ignore


if __name__ == "__main__":  # pragma: no cover
    web_site_main()
