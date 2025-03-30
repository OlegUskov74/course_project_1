import datetime
import os
import pytest
import requests
from typing import Any
from unittest.mock import patch

from src.utils import (get_welcome_text,
                       main_cards, read_finance_excel_operation,
                       top_transactions,
                       get_api_currency,
                       get_api_stocks,
                       currency_rates,
                       open_user_settings)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_open_user_settings() -> None:
    """
    [Тест] Функция чтения пользовательских настроек.
    """
    data = open_user_settings()
    assert data == {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}


def test_open_user_settings_error() -> None:
    """
    [Тест] Функция чтения пользовательских настроек.
    Выбрасывает ошибку Exception ("Файл отсутствует")
    """
    with pytest.raises(Exception) as f_open:
        open_user_settings("fake_file")
        assert str(f_open) == "Файл отсутствует"


@pytest.mark.parametrize("test_datetime, result", [("2025-03-18 08:00:23", "Доброе утро"),
                                                   ("2025-03-16 13:00:23", "Добрый день"),
                                                   ("2025-02-11 18:00:23", "Добрый вечер"),
                                                   ("2023-10-12 23:00:23", "Доброй ночи")])
def test_get_welcome_text(test_datetime: str, result: str) -> None:
    """
    [Тест] Функция возврата строки приветствия по дате форматом YYYY-MM-DD HH:MM:SS.
    """
    assert get_welcome_text(test_datetime) == result

# тест падает
def test_read_finance_excel_operation_range() -> None:
    """
    [Тест] Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    """
    success_test = read_finance_excel_operation("2021-07-02 18:25:14", ROOT_DIR + "/data/operations.xlsx")
    assert isinstance(success_test, list)


def test_main_cards(excel_data: list[dict]) -> None:
    """
    [Тест] Функция вывода всей информации по картам.
    """
    data = main_cards(excel_data)
    assert data == [{"cashback": 0.0, "last_digits": "7197", "total_spent": 8023.92}]

    with pytest.raises(Exception):
        main_cards([{}])


def test_top_transactions(excel_data: list[dict]) -> None:
    """
    [Тест] Функция возврата ТОП 5 транзакций.
    """
    data = top_transactions(excel_data)
    assert data == [
        {
            "amount": 115909.42,
            "category": "Переводы",
            "date": "24.01.2018",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"amount": 9700.0, "category": "Пополнения", "date": "25.01.2018", "description": "Перевод с карты"},
        {"amount": 5748.0, "category": "Авиабилеты", "date": "25.01.2018", "description": "Aviacassa"},
        {"amount": 840.3, "category": "Ж/д билеты", "date": "24.01.2018", "description": "РЖД"},
        {"amount": 376.0, "category": "Транспорт", "date": "25.01.2018", "description": "Яндекс Такси"},
    ]


@patch("requests.get")
def test_get_api_currency(requests_mock: Any) -> None:
    """
    [Тест] Функция отправляет запрос API и возвращает курс валют
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"rates": {"RUB": 1.887787}}
    data = get_api_currency("USD")
    assert data == 1.887787

    requests_mock.return_value.status_code = 500
    data = get_api_currency("USD")
    assert data == 0

    requests_mock.side_effect = requests.exceptions.ReadTimeout
    with pytest.raises(requests.exceptions.ReadTimeout):
        get_api_currency("USD")


@patch("requests.get")
def test_currency_rates(requests_mock: Any) -> None:
    """
    [Тест] Функция возвращает курс валют согласно пользовательскому запросу.
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"rates": {"RUB": 32.223}}

    data = currency_rates()
    assert data == [{"currency": "USD", "rate": 32.22}, {"currency": "EUR", "rate": 32.22}]



# Тест падает
@patch("requests.get")
def test_get_api_stocks(requests_mock: Any) -> None:
    """
    [Тест] Функция отправляет запрос API и возвращает стоймость акций по категориям
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = [{"price": 32.223}]
    data = get_api_stocks("USD")
    assert data == 32.223

    # requests_mock.return_value.status_code = 200
    # requests_mock.return_value.json.return_value = [{"price": 32.223}]
    # with pytest.raises(Exception):
    #     get_api_stocks("USD")
    #
    # requests_mock.return_value.status_code = 500
    # data = get_api_stocks("USD")
    # assert data == 0


# Тест падает
@patch("requests.get")
def test_user_stocks(requests_mock: Any) -> None:
    """
    [Тест] Функция возвращает стоймость акций согласно пользовательскому запросу.
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = [{"price": 322.223}]
    data = get_api_stocks("USD")
    assert data == 322.223

