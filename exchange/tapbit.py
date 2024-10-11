import time
import hmac
import hashlib
import requests
from typing import Dict, Any
from datetime import datetime

import os
from dataclasses import dataclass

class Tapbit:
    def __init__(self, api_key: str, secret_key: str, passphrase: str = None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://openapi.tapbit.com"
        self.position_mode = "one-way"  # 기본값
        self.order_info = None
        self.time_offset = 0
        self._sync_time()

    def _get_signature(self, timestamp: str, method: str, endpoint: str, body: str = '') -> str:
        message = f"{timestamp}{method}{endpoint}{body}"
        return hmac.new(self.secret_key.encode('utf-8'), 
                        message.encode('utf-8'), 
                        hashlib.sha256).hexdigest()
    
    def _sync_time(self):
        response = self._request("GET", "/spot/api/spot/time")
        server_time_str = response['timestamp']
        
        server_time = int(datetime.strptime(server_time_str, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp() * 1000)
        local_time = int(time.time() * 1000)
        self.time_offset = server_time - local_time

    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        url = self.base_url + endpoint
        timestamp = str(int(time.time() * 1000) + self.time_offset)
        signature = self._get_signature(timestamp, method, endpoint, str(data or ''))
        
        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
        
        response = requests.request(method, url, headers=headers, params=params, json=data)
        return response.json()

    # Market 데이터 조회
    def fetch_ticker(self, symbol: str) -> Dict:
        return self._request("GET", "/spot/api/spot/instruments/ticker_one", {"instrument_id": symbol})

    def fetch_orderbook(self, symbol: str, depth: int = 10) -> Dict:
        return self._request("GET", "/spot/api/spot/instruments/depth", 
                            {"instrument_id": symbol, "depth": depth})

    def fetch_klines(self, symbol: str, timeframe: str, 
                    start_time: int = None, end_time: int = None) -> Dict:
        params = {
            "instrument_id": symbol,
            "period": timeframe
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return self._request("GET", "/spot/api/spot/instruments/candles", params)

    # 거래
    def create_order(self, symbol: str, type: str, side: str, 
                    amount: float, price: float = None, params: Dict = {}) -> Dict:
        data = {
            "instrument_id": symbol,
            "direction": "1" if side == "buy" else "2",
            "quantity": str(amount)
        }
        if price:
            data["price"] = str(price)
        
        return self._request("POST", "/spot/api/v1/spot/order", data=data)

    def cancel_order(self, order_id: str) -> Dict:
        return self._request("POST", "/spot/api/v1/spot/cancel_order", data={"order_id": order_id})

    # 잔고 관련
    def fetch_balance(self) -> Dict:
        return self._request("GET", "/spot/api/v1/spot/account/list")

    def fetch_open_orders(self, symbol: str) -> Dict:
        return self._request("GET", "/spot/api/v1/spot/open_order_list", {"instrument_id": symbol})
    


    def init_info(self, order_info: Any):
        self.order_info = order_info

    def get_amount(self, order_info: Any) -> float:
        if order_info.amount is not None:
            return order_info.amount
        elif order_info.percent is not None:
            # Implement logic to calculate amount based on percentage
            # This might require fetching account balance or position information
            pass
        else:
            raise ValueError("Either amount or percent must be specified")

    def market_entry(self, order_info: Any):
        symbol = order_info.unified_symbol
        side = "1" if order_info.side == "buy" else "2"
        amount = self.get_amount(order_info)

        data = {
            "instrument_id": symbol,
            "direction": side,
            "quantity": str(amount),
            "order_type": "1"  # Assuming 1 is for market orders
        }

        if self.position_mode == "hedge":
            # Add position side for hedge mode if supported by Tapbit
            pass

        return self._request("POST", "/spot/api/v1/spot/order", data=data)

    def market_close(self, order_info: Any):
        symbol = order_info.unified_symbol
        side = "1" if order_info.side == "buy" else "2"
        amount = self.get_amount(order_info)

        data = {
            "instrument_id": symbol,
            "direction": side,
            "quantity": str(amount),
            "order_type": "1",  # Assuming 1 is for market orders
            "reduce_only": "true"
        }

        if self.position_mode == "hedge":
            # Add position side for hedge mode if supported by Tapbit
            pass

        return self._request("POST", "/spot/api/v1/spot/order", data=data)

    def market_buy(self, order_info: Any):
        symbol = order_info.unified_symbol
        amount = self.get_amount(order_info)

        data = {
            "instrument_id": symbol,
            "direction": "1",  # 1 for buy
            "quantity": str(amount),
            "order_type": "1"  # Assuming 1 is for market orders
        }

        return self._request("POST", "/spot/api/v1/spot/order", data=data)

    def market_sell(self, order_info: Any):
        symbol = order_info.unified_symbol
        amount = self.get_amount(order_info)

        data = {
            "instrument_id": symbol,
            "direction": "2",  # 2 for sell
            "quantity": str(amount),
            "order_type": "1"  # Assuming 1 is for market orders
        }

        return self._request("POST", "/spot/api/v1/spot/order", data=data)

    def set_leverage(self, leverage: int, symbol: str):
        # Implement if Tapbit supports setting leverage
        pass

    def get_balance(self, base: str):
        balances = self._request("GET", "/spot/api/v1/spot/account/list")
        for balance in balances:
            if balance['currency'] == base:
                return float(balance['available'])
        return 0.0

    def get_price(self, symbol: str):
        ticker = self.fetch_ticker(symbol)
        return float(ticker['last'])

    def get_futures_position(self, symbol=None, all=False):
        # Implement if Tapbit supports futures trading
        pass

@dataclass
class MarketOrder:
    unified_symbol: str
    side: str
    amount: float = None
    percent: float = None
    is_entry: bool = False
    is_close: bool = False
    is_buy: bool = False
    is_sell: bool = False

def main():
    print("Tapbit API 테스트 시작!")

    # API 키와 시크릿 키를 환경 변수에서 가져옵니다.
    api_key = "7dcf3f91a6374843022b7e2488b701b5"
    secret_key = "5884f79b1dc745b0b1020544f8fa0f3a"

    if not api_key or not secret_key:
        print("API 키와 시크릿 키를 환경 변수에 설정해주세요.")
        return

    tapbit = Tapbit(api_key, secret_key)

    # 테스트용 주문 정보
    test_order = MarketOrder(
        unified_symbol="BTC-USDT",
        side="buy",
        amount=0.001,  # 작은 금액으로 테스트
        is_buy=True
    )

    tapbit.init_info(test_order)

    # market_buy 테스트
    print("\n테스트 1: market_buy")
    try:
        result = tapbit.market_buy(test_order)
        print(f"market_buy 결과: {result}")
    except Exception as e:
        print(f"market_buy 오류: {str(e)}")

    # # market_sell 테스트
    # print("\n테스트 2: market_sell")
    # test_order.side = "sell"
    # test_order.is_buy = False
    # test_order.is_sell = True
    # try:
    #     result = tapbit.market_sell(test_order)
    #     print(f"market_sell 결과: {result}")
    # except Exception as e:
    #     print(f"market_sell 오류: {str(e)}")

    # # market_entry 테스트
    # print("\n테스트 3: market_entry")
    # test_order.side = "buy"
    # test_order.is_buy = True
    # test_order.is_sell = False
    # test_order.is_entry = True
    # try:
    #     result = tapbit.market_entry(test_order)
    #     print(f"market_entry 결과: {result}")
    # except Exception as e:
    #     print(f"market_entry 오류: {str(e)}")

    # # market_close 테스트
    # print("\n테스트 4: market_close")
    # test_order.side = "sell"
    # test_order.is_buy = False
    # test_order.is_sell = True
    # test_order.is_entry = False
    # test_order.is_close = True
    # try:
    #     result = tapbit.market_close(test_order)
    #     print(f"market_close 결과: {result}")
    # except Exception as e:
    #     print(f"market_close 오류: {str(e)}")

    print("\nTapbit API 테스트 완료!")

if __name__ == "__main__":
    main()