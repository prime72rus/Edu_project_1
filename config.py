from pathlib import Path

PATH = Path(__file__).parent
PATH_TO_OPERATIONS = PATH / "data" / "operations.xlsx"  # путь к файлу с транзакциями
PATH_TO_USER_SETTINGS = PATH / "user_settings.json"  # путь к файлу пользовательских настроек
PATH_TO_LOGGER = PATH / "logs"  # путь к каталогу лог-файлов
PATH_TO_REPORTS = PATH / "reports"  # путь к каталогу сохранения отчетов