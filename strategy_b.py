import time
from notifier import send_telegram
import requests

class Strategy:
    def __init__(self, trader):
        self.trader = trader
        self.entry_price = None
        self.position = 0
        self.status = "Idle"
        self.current_leverage = 3
        self.fee_rate = 0.0002

    def get_history_prices(self, limit=30):
        url = f"https://www.okx.com/api/v5/market/candles?instId={self.trader.config['symbol']}&bar=1m&limit={limit}"
        res = requests.get(url).json()
        prices = [float(p[4]) for p in res['data']]
        return list(reversed(prices))

    def compute_volatility(self, prices):
        if len(prices) < 2:
            return 0
        returns = [(prices[i+1] - prices[i]) / prices[i] for i in range(len(prices)-1)]
        return sum(abs(r) for r in returns) / len(returns)

    def dynamic_leverage(self, volatility):
        if volatility < 0.005:
            return 5
        elif volatility < 0.01:
            return 3
        else:
            return 2

    def trend_signal(self):
        prices = self.get_history_prices()
        if len(prices) < 20:
            return None, 3
        sma = sum(prices[-20:]) / 20
        current = prices[-1]
        vol = self.compute_volatility(prices)
        lev = self.dynamic_leverage(vol)
        if current > sma:
            return "buy", lev
        elif current < sma:
            return "sell", lev
        return None, lev

    def run_loop(self):
        print("[STRATEGY] Running strategy loop...")
        while True:
            price = self.trader.get_price()
            if price is None:
                time.sleep(5)
                continue
            print(f"[MARKET] Current price: {price}")

            balance = self.trader.get_balance()
            if balance == 0:
                print("[WARN] Balance zero or failed to fetch, skipping trade.")
                time.sleep(10)
                continue

            risk_percent = self.trader.config.get("risk_percent", 0.05)
            max_drawdown = self.trader.config.get("max_drawdown_ratio", 0.15)
            profit_target = self.trader.config.get("daily_profit_target", 0.05)

            lev = self.current_leverage
            max_size = balance * risk_percent / (1 + 2 * self.fee_rate) * lev
            size = round(max_size, 4)

            self.status = "Waiting"
            if self.trader.config.get("strategy") == "trend":
                signal, lev = self.trend_signal()
                self.current_leverage = lev
                if signal == "buy" and self.position == 0 and size > 0:
                    self.entry_price = price
                    self.trader.buy(size, lev)
                    self.position = 1
                    self.status = f"Trend Buy (x{lev})"
                    send_telegram(f"📈 Buy @ {price} | Size: {size} | Leverage: {lev}x")
                elif signal == "sell" and self.position == 1 and size > 0:
                    self.trader.sell(size, lev)
                    self.position = 0
                    self.status = f"Trend Sell (x{lev})"
                    send_telegram(f"📉 Sell @ {price} | Size: {size} | Leverage: {lev}x")

            if self.entry_price and price < self.entry_price * (1 - max_drawdown):
                send_telegram(f"⚠️ Drawdown Alert: {price} < -{max_drawdown*100}% from {self.entry_price}")

            time.sleep(10)