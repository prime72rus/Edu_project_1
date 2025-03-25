from config import PATH_TO_OPERATIONS
from src.views import web_site_main
from src.services import search_translations
from src.reports import spending_by_category
from src.utils import checking_date_from_user, read_xlsx


def main() -> None:
    """
    Функция запуска приложения
    """
    while True:
        user_input = input("Введите дату в формате YYYY-MM-DD HH:MM:SS: ")
        try:
            data_str = checking_date_from_user(user_input)
        except ValueError:
            print("Дата не соответствует формату!")
            continue
        else:
            break

    web_site_main(user_input)
    print("\nПереводы физлицам:\n")
    search_translations()
    print("\nТраты по категориям:\n")
    data_df = read_xlsx(PATH_TO_OPERATIONS)
    user_input_category = input("Введите наименование категории: ")
    date = data_str.split(" ")[0]
    spending_by_category(data_df, user_input_category, date)


if __name__ == "__main__":
    main()

