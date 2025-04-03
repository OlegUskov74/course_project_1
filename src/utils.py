import json
import os
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import requests
from dotenv import load_dotenv

from config import ROOT_DIR

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_FMP = os.getenv("API_FMP")


def open_user_settings(user_settings: str = ROOT_DIR + "/data/user_settings.json") -> Dict[str, Any]:
    """
    Функция открывает пользовательский запрос в формате .json
    :param user_settings: файл json
    :return: отрытый файл в формате словарь списков
    """
    try:
        with open(user_settings, 'r') as json_file:
            data = json.load(json_file)
        return data
    except:
        raise Exception("Файл отсутствует")


def get_welcome_text(user_datetime: str) -> str:
    """
    Функция возврата строки приветствия по дате форматом YYYY-MM-DD HH:MM:SS
    """
    date_and_time = datetime.strptime(user_datetime, "%Y-%m-%d %H:%M:%S")
    hour = date_and_time.hour

    if 4 <= hour <= 11:
        welcome = "Доброе утро"
    elif 12 <= hour < 17:
        welcome = "Добрый день"
    elif 17 <= hour < 22:
        welcome = "Добрый вечер"
    else:
        welcome = "Доброй ночи"

    return welcome


def read_finance_excel_operation(date: str, filename: str = ROOT_DIR + "/data/operations.xlsx") -> list[dict]:
    """
    Функция фильтрует файл по дате и возвращает список транзакций
    :param date: формат времени в виде "%Y-%m-%d %H:%M:%S"
    :param filename: имя файла xlsx
    :return: список транзакций
    """
    format_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date, end_date = format_date.replace(day=1), format_date

    excel_data = pd.read_excel(filename)
    group_data = excel_data.to_dict("records")
    filtered_data = [
        data
        for data in list(group_data)
        if start_date <= datetime.strptime(data["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
    ]
    return list(filtered_data)


def main_cards(data: list[dict]) -> list:
    """
    Функция вывода информации по карте
    :param data: список транзакций
    :return: информация по транзакциям
    """

    df = pd.DataFrame(data)
    cards = []

    add_group_data = df.groupby("Номер карты").agg({"Сумма операции с округлением": "sum", "Кэшбэк": "sum"})
    for card_num, row in add_group_data.iterrows():
        info_card = {
            "last_digits": str(card_num)[-4:],
            "total_spent": float(row["Сумма операции с округлением"]),
            "cashback": float(row["Кэшбэк"]),
        }
        cards.append(info_card)
    return cards


def top_transactions(data: list[dict]) -> list:
    """
    Функция выдает топ-5 транзакций по сумме платежа
    """
    top_transaction = []
    df = pd.DataFrame(data)
    top_data = df.sort_values(by="Сумма операции с округлением", ascending=False).head(5)
    for data, row in top_data.iterrows():
        top_transaction.append(
            {
                "date": row["Дата платежа"],
                "amount": float(row["Сумма операции с округлением"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    return top_transaction


def get_api_currency(currency: str) -> float:
    """
    Функция отправляет запрос API и возвращает курс валют
    """
    url = "https://api.apilayer.com/exchangerates_data/latest"

    payload = {'symbols': "RUB", "base": currency}
    headers = {"apikey": API_KEY}

    response = requests.get(url, headers=headers, params=payload)
    status_code = response.status_code
    if status_code == 200:
        result = response.json()
        return float(result["rates"]["RUB"])
    else:
        return 0


def currency_rates() -> list:
    """
    Функция возвращает курс валют согласно пользовательскому запросу
    """
    user_settings = open_user_settings()
    user_currencies = user_settings["user_currencies"]
    data_rates = []
    for currency in user_currencies:
        rates = get_api_currency(currency)
        data_rates.append({"currency": currency, "rate": round(rates, 2)})
    return data_rates


def get_api_stocks(stock: str) -> Any:
    """
    Функция отправляет запрос API и возвращает стоймость акций по категориям
    """
    url = "https://financialmodelingprep.com/stable/historical-price-eod/light"

    payload = {'symbol': stock,
               "apikey": API_FMP}
    response = requests.get(url, params=payload)
    status_code = response.status_code
    if status_code == 200:
        result = response.json()
        return result[0]['price']
    else:
        return 0.0


def user_stocks() -> list:
    """
    Функция возвращает стоймость акций согласно пользовательскому запросу
    """
    user_settings = open_user_settings()
    user_stock = user_settings["user_stocks"]
    data_stocks = []
    for stocks in user_stock:
        stock = get_api_stocks(stocks)
        data_stocks.append({"stock": stocks, "price": round(stock, 2)})
    return data_stocks

# if __name__ == "__main__":
#     print(user_stocks())
