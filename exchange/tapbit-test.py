import requests
import time
import hmac
import hashlib

# API 설정
BASE_URL = "https://openapi.tapbit.com/"
API_KEY = "7dcf3f91a6374843022b7e2488b701b5"
SECRET_KEY = "5884f79b1dc745b0b1020544f8fa0f3a"

def get_signature(timestamp, method, endpoint, body=''):
    """
    API 요청에 필요한 서명을 생성합니다.
    """
    message = f"{timestamp}{method}{endpoint}{body}"
    return hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

def make_request(method, endpoint, params=None, data=None):
    """
    API 요청을 보내고 응답을 반환합니다.
    """
    url = BASE_URL + endpoint
    timestamp = str(int(time.time() * 1000))
    signature = get_signature(timestamp, method, endpoint, str(data or ''))
    
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    
    return response.json()

def get_server_time():
    """
    서버 시간을 조회합니다.
    """
    return make_request("GET", "swap/api/v1/usdt/time")

def get_contract_list():
    """
    계약 목록을 조회합니다.
    """
    return make_request("GET", "swap/api/usdt/instruments/list")

def get_order_book(instrument_id, depth=10):
    """
    주문서를 조회합니다.
    """
    params = {"instrument_id": instrument_id, "depth": depth}
    return make_request("GET", "swap/api/usdt/instruments/depth", params)

def get_kline_data(instrument_id, start_time, end_time, period):
    """
    K라인 데이터를 조회합니다.
    """
    params = {
        "instrument_id": instrument_id,
        "start_time": start_time,
        "end_time": end_time,
        "period": period
    }
    return make_request("GET", "swap/api/usdt/instruments/candles", params)

def get_ticker(instrument_id):
    """
    특정 계약의 티커 정보를 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "swap/api/usdt/instruments/ticker_one", params)

def get_ticker_list():
    """
    모든 계약의 티커 정보 리스트를 조회합니다.
    """
    return make_request("GET", "swap/api/usdt/instruments/ticker_list")

def get_funding_rate(instrument_id):
    """
    특정 계약의 자금 이율을 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "swap/api/usdt/instruments/funding_rate", params)

def get_recent_trades(instrument_id):
    """
    최근 거래 목록을 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "swap/api/usdt/instruments/trade_list", params)

# Spot Market API 함수들
def get_spot_instrument_info(instrument_id):
    """
    특정 스팟 거래쌍의 정보를 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "spot/api/spot/instruments/trade_pair_one", params)

def get_spot_instruments_list():
    """
    모든 스팟 거래쌍 정보를 조회합니다.
    """
    return make_request("GET", "spot/api/spot/instruments/trade_pair_list")

def get_spot_order_book(instrument_id, depth=10):
    """
    스팟 주문서를 조회합니다.
    """
    params = {"instrument_id": instrument_id, "depth": depth}
    return make_request("GET", "spot/api/spot/instruments/depth", params)

def get_spot_ticker(instrument_id):
    """
    특정 스팟 거래쌍의 티커 정보를 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "spot/api/spot/instruments/ticker_one", params)

def get_spot_ticker_list():
    """
    모든 스팟 거래쌍의 티커 정보를 조회합니다.
    """
    return make_request("GET", "spot/api/spot/instruments/ticker_list")

def get_spot_kline_data(instrument_id, period, start_time=None, end_time=None):
    """
    스팟 K라인 데이터를 조회합니다.
    """
    params = {
        "instrument_id": instrument_id,
        "period": period
    }
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    return make_request("GET", "spot/api/spot/instruments/candles", params)

def get_spot_recent_trades(instrument_id):
    """
    스팟 최근 거래 목록을 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    return make_request("GET", "spot/api/spot/instruments/trade_list", params)

def get_asset_list(currency=None):
    """
    자산 목록을 조회합니다.
    """
    params = {}
    if currency:
        params["currency"] = currency
    return make_request("GET", "spot/api/spot/instruments/asset/list", params)

# Account API 함수들

def get_spot_account_list():
    """
    스팟 계정 정보를 조회합니다.
    """
    return make_request("GET", "spot/api/v1/spot/account/list")

def get_spot_account_one(asset):
    """
    특정 자산의 스팟 계정 정보를 조회합니다.
    """
    params = {"asset": asset}
    return make_request("GET", "spot/api/v1/spot/account/one", params)

# Order API 함수들

def place_spot_order(instrument_id, direction, price, quantity):
    """
    스팟 주문을 생성합니다.
    """
    data = {
        "instrument_id": instrument_id,
        "direction": direction,
        "price": price,
        "quantity": quantity
    }
    return make_request("POST", "spot/api/v1/spot/order", data=data)

def place_batch_spot_orders(orders):
    """
    여러 개의 스팟 주문을 한 번에 생성합니다.
    """
    return make_request("POST", "spot/api/v1/spot/batch_order", data=orders)

def cancel_spot_order(order_id):
    """
    스팟 주문을 취소합니다.
    """
    data = {"order_id": order_id}
    return make_request("POST", "spot/api/v1/spot/cancel_order", data=data)

def batch_cancel_spot_orders(order_ids):
    """
    여러 개의 스팟 주문을 한 번에 취소합니다.
    """
    data = {"orderIds": order_ids}
    return make_request("POST", "spot/api/v1/spot/batch_cancel_order", data=data)

def get_open_spot_orders(instrument_id, next_order_id=None):
    """
    미체결 스팟 주문 목록을 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    if next_order_id:
        params["next_order_id"] = next_order_id
    return make_request("GET", "spot/api/v1/spot/open_order_list", params)

def get_closed_spot_orders(instrument_id, next_order_id=None):
    """
    완료된 스팟 주문 목록을 조회합니다.
    """
    params = {"instrument_id": instrument_id}
    if next_order_id:
        params["next_order_id"] = next_order_id
    return make_request("GET", "spot/api/v1/spot/closed_order_list", params)

def get_spot_order_info(order_id):
    """
    특정 스팟 주문의 정보를 조회합니다.
    """
    params = {"order_id": order_id}
    return make_request("GET", "spot/api/v1/spot/order_info", params)

def main():
    print("api test 시작!!")
    # print("1. 서버 시간 조회")
    # print(get_server_time())
    # print("\n2. 계약 목록 조회")
    # print(get_contract_list())
    # print("\n3. ETH-SWAP 주문서 조회")
    # print(get_order_book("ETH-SWAP"))
    # print("\n4. BTC-SWAP K라인 데이터 조회")
    # print(get_kline_data("BTC-SWAP", "1681120800000", "1681207200000", "60"))
    # print("\n5. BTC-SWAP 티커 정보 조회")
    # print(get_ticker("BTC-SWAP"))
    # print("\n6. 전체 티커 리스트 조회")
    # print(get_ticker_list())
    # print("\n7. BTC-SWAP 자금 이율 조회")
    # print(get_funding_rate("BTC-SWAP"))
    # print("\n8. BTC-SWAP 최근 거래 목록 조회")
    # print(get_recent_trades("BTC-SWAP"))
    # 분리
    # print("\n=== Spot Market API Tests ===")
    # print("\n9. BTC/USDT 스팟 거래쌍 정보 조회")
    # print(get_spot_instrument_info("BTC/USDT"))
    # print("\n10. 스팟 거래쌍 목록 조회")
    # print(get_spot_instruments_list())
    # print("\n11. BTC/USDT 스팟 주문서 조회")
    # print(get_spot_order_book("BTC/USDT"))
    # print("\n12. BTC 자산 정보 조회")
    # print(get_asset_list("BTC"))

if __name__ == "__main__":
    main()