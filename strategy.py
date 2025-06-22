import time
from notifier import send_telegram
import requests

def adjusted_trade_size(balance, risk_percent, leverage, fee_rate, min_fee):
    max_size = balance * risk_percent * leverage
    min_size = min_fee / fee_rate if fee_rate > 0 else 0
    final_size = max(max_size, min_size)
    final_size = min(final_size, balance * leverage)
    return round(final_size, 4)

class Strategy:
    def __init__(self, trader):
        self.trader = trader
        self.entry_price = None
        self.position = 0
        self.status = "Idle"
        self.current_leverage = 2
        self.fee_rate = 0.001
        self.min_fee = 0.02

    def get_history_prices(self, limit=60):
        url = f"https://www.okx.com/api/v5/market/candles?instId={self.trader.config['symbol']}&bar=1m&limit={limit}"
        res = requests.get(url).json()
        prices = [float(p[4]) for p in res['data']]
        return list(reversed(prices))

    def compute_volatility(self, prices):
        returns = [(prices[i+1] - prices[i]) / prices[i] for i in range(len(prices)-1)]
        return sum(abs(r) for r in returns) / len(returns)

    def dynamic_leverage(self, volatility):
        if volatility < 0.004:
            return 3
        elif volatility < 0.008:
            return 2
        return 1

    def trend_signal(self):
        prices = self.get_history_prices(60)
        if len(prices) < 50:
            return None, 2

        sma20 = sum(prices[-20:]) / 20
        sma50 = sum(prices[-50:]) / 50
        current_price = prices[-1]

        vol = self.compute_volatility(prices)
        lev = self.dynamic_leverage(vol)

        # 趋势判断：金叉/死叉确认
        if sma20 > sma50 and current_price > sma20:
            return "buy", lev
        elif sma20 < sma50 and current_price < sma20:
            return "sell", lev
        return None, lev

    def run_loop(self):
        print("[STRATEGY] Running strategy loop...")
        while True:
            price = self.trader.get_price()
            if price is None:
                time.sleep(5)
                continue

            balance = self.trader.get_balance()
            if balance == 0:
                time.sleep(10)
                continue

            risk_percent = self.trader.config.get("risk_percent", 0.02)
            max_drawdown = self.trader.config.get("max_drawdown_ratio", 0.05)
            profit_target = self.trader.config.get("daily_profit_target", 0.03)

            self.status = "Waiting"

            signal, lev = None, 2
            if self.trader.config.get("strategy") == "trend":
                signal, lev = self.trend_signal()
                self.current_leverage = lev

            size = adjusted_trade_size(balance, risk_percent, lev, self.fee_rate, self.min_fee)

            if signal == "buy" and self.position == 0 and size > 0:
                self.entry_price = price
                self.trader.buy(size, lev)
                self.position = 1
                self.status = f"Buy Open (x{lev})"
                send_telegram(f"📈 开多单 @ {price} | Size: {size} | Leverage: {lev}x")

            elif signal == "sell" and self.position == 1:
                self.trader.sell(size, lev)
                pnl = price - self.entry_price
                percent = pnl / self.entry_price * 100
                self.position = 0
                self.status = f"Sell Close"
                send_telegram(f"📉 平多单 @ {price} | PnL: {pnl:.2f} ({percent:.2f}%)")

            # 自动止损平仓
            if self.entry_price and self.position == 1:
                if price < self.entry_price * (1 - max_drawdown):
                    self.trader.sell(size, lev)
                    self.position = 0
                    self.status = "Stopped"
                    send_telegram(f"⚠️ 止损出场 @ {price} < -{max_drawdown*100}% from {self.entry_price}")

                elif price > self.entry_price * (1 + profit_target):
                    self.trader.sell(size, lev)
                    self.position = 0
                    self.status = "Take Profit"
                    send_telegram(f"✅ 达到盈利目标 @ {price} > +{profit_target*100}% from {self.entry_price}")

            time.sleep(30)  # 拉长周期，避免频繁交易
