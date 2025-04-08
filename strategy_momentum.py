def calculate_investment_percentage(current_price, moving_avg):
    if current_price > moving_avg:
        return 1.2
    else:
        return 0.8