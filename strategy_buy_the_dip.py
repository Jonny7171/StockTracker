def calculate_investment_percentage(current_price, moving_avg):
    deviation = (current_price - moving_avg) / moving_avg
    if deviation <= -0.03:
        return 1.5
    elif deviation <= -0.02:
        return 1.25
    elif deviation <= -0.01:
        return 1.1
    elif deviation <= 0.005:
        return 1.0
    elif deviation <= 0.02:
        return 0.9
    else:
        return 0.75