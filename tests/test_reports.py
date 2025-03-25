from datetime import datetime, timedelta

import pandas as pd
import pytest
from unittest.mock import patch

from src.reports import spending_by_category, save_to_file_default, save_to_file


@pytest.fixture
def sample_data():
    data = {
        "Дата операции": [
            "24.12.2021 18:18:27",
            "23.11.2021 22:33:11",
            "25.10.2021 16:07:27",
        ],
        "Категория": ["Фастфуд", "Каршеринг", "Фастфуд"],
        "Сумма платежа": [-34.00, -1.51, -130.00],
    }
    return pd.DataFrame(data)


@pytest.fixture
def tmp_report_dir(tmp_path):
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    return report_dir


def test_spending_by_category(sample_data):
    result = spending_by_category(sample_data, category="Фастфуд", date="2021-12-31")
    assert isinstance(result, pd.DataFrame)

    expected_dates = ["24.12.2021 18:18:27", "23.11.2021 22:33:11", "25.10.2021 16:07:27"]
    result["Дата операции"] = result["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")
    assert result["Дата операции"].isin(expected_dates).all()
    assert result["Категория"].unique() == ["Фастфуд"]


@patch("src.reports.datetime")
def test_spending_by_category_no_date(mock_datetime, sample_data):
    mock_current_date = datetime(2021, 12, 24)
    mock_datetime.now.return_value = mock_current_date

    result = spending_by_category(sample_data, category="Фастфуд")

    assert isinstance(result, pd.DataFrame)

    assert result["Категория"].unique() == ["Фастфуд"]


def test_save_to_file_default(sample_data, tmp_report_dir):
    @save_to_file_default
    def test_func(transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions

    with patch("src.reports.PATH_TO_REPORTS", str(tmp_report_dir)):
        result = test_func(sample_data)

    files = list(tmp_report_dir.glob("*.xlsx"))
    assert len(files) == 1
    file_path = files[0]

    saved_data = pd.read_excel(file_path)
    pd.testing.assert_frame_equal(saved_data, result)


def test_save_to_file(sample_data, tmp_report_dir):
    filename = "test_output"

    @save_to_file(filename)
    def test_func(transactions: pd.DataFrame) -> pd.DataFrame:
        return transactions

    with patch("src.reports.PATH_TO_REPORTS", str(tmp_report_dir)):
        result = test_func(sample_data)

    file_path = tmp_report_dir / f"{filename}.xlsx"
    assert file_path.exists()

    saved_data = pd.read_excel(file_path)
    pd.testing.assert_frame_equal(saved_data, result)
