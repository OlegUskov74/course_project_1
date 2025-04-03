from src.utils import get_welcome_text, read_finance_excel_operation, main_cards, top_transactions, currency_rates, \
    user_stocks


def main(date: str) -> dict:
    """Основная функция запуска"""
    welcome = get_welcome_text(date)
    struct_file_json = read_finance_excel_operation(date)

    json_response = {
        "greeting": welcome,
        "cards": main_cards(struct_file_json),
        "top_transactions": top_transactions(struct_file_json),
        "currency_rates": currency_rates(),
        "stock_prices": user_stocks(),
    }

    return json_response
