import requests
import hmac
import hashlib
import base64
import datetime
import json

class Trader:
    def __init__(self, config):
        self.config = config

    def _signature(self, timestamp, method, request_path, body=""):
        message = f"{timestamp}{method}{request_path}{body}"
        mac = hmac.new(self.config['secret_key'].encode(), message.encode(), hashlib.sha256)
        return base64.b64encode(mac.digest()).decode()

    def _headers(self, method, request_path, body=""):
        timestamp = datetime.datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        sign = self._signature(timestamp, method, request_path, body)
        return {
            'OK-ACCESS-KEY': self.config['api_key'],
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.config['passphrase'],
            'Content-Type': 'application/json'
        }

    def get_price(self):
        url = f"{self.config['base_url']}/api/v5/market/ticker?instId={self.config['symbol']}"
        try:
            res = requests.get(url)
            data = res.json()
            return float(data['data'][0]['last'])
        except:
            print("[ERROR] Failed to fetch price.")
            return None

    def get_balance(self):
        path = "/api/v5/account/balance"
        url = self.config['base_url'] + path
        headers = self._headers("GET", path)
        try:
            res = requests.get(url, headers=headers)
            data = res.json()
            if data.get("code") != "0":
                print(f"[ERROR] API returned error code: {data.get('code')}, msg: {data.get('msg')}")
                return 0
            account_data = data.get("data", [])
            if not account_data:
                print("[ERROR] No account data found.")
                return 0
            for account in account_data:
                # 这里重点是进入 details 找 USDT
                for asset in account.get("details", []):
                    if asset.get("ccy") == "USDT":
                        return float(asset.get("availBal", 0))
            print("[WARN] USDT balance not found in account details.")
        except Exception as e:
            print("[ERROR] Failed to fetch balance:", e)
        return 0




    def order(self, side, size, leverage):
        path = "/api/v5/trade/order"
        url = self.config['base_url'] + path
        body = json.dumps({
            "instId": self.config['symbol'],
            "ccy": "USDT",
            "tdMode": "isolated",
            "side": side,
            "ordType": "market",
            "sz": str(size),
            "lever": str(leverage)
        })
        headers = self._headers("POST", path, body)
        try:
            res = requests.post(url, headers=headers, data=body)
            print("[ORDER] Response:", res.json())
        except Exception as e:
            print("[ERROR] Order failed:", e)

    def buy(self, size, leverage=3):
        print(f"[TRADE] Buy {size} {self.config['symbol']} at {leverage}x")
        self.order("buy", size, leverage)

    def sell(self, size, leverage=3):
        print(f"[TRADE] Sell {size} {self.config['symbol']} at {leverage}x")
        self.order("sell", size, leverage)