import csv
import os
from datetime import datetime

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def log_trade(timestamp, side, price, size, leverage, status, response):
    ensure_dir("logs")
    filepath = "logs/trade_log.csv"
    header = ["timestamp", "side", "price", "size", "leverage", "status", "response"]
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([timestamp, side, price, size, leverage, status, response])

def log_price(timestamp, price, sma20, volatility, signal):
    ensure_dir("logs")
    filepath = "logs/price_log.csv"
    header = ["timestamp", "price", "sma20", "volatility", "signal"]
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([timestamp, price, sma20, volatility, signal])

def log_equity(timestamp, equity):
    ensure_dir("logs")
    filepath = "logs/equity_log.csv"
    header = ["timestamp", "equity_usdt"]
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow([timestamp, equity])