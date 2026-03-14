"""
orders.py - Order placement logic for Binance Futures Testnet
"""

from bot.client import BinanceClient
from bot.logging_config import get_logger

logger = get_logger(__name__)


def build_order_params(validated: dict) -> dict:
    """Build the order parameter dict from validated inputs."""
    params = {
        "symbol": validated["symbol"],
        "side": validated["side"],
        "type": validated["order_type"],
        "quantity": validated["quantity"],
    }

    order_type = validated["order_type"]

    if order_type == "LIMIT":
        params["price"] = validated["price"]
        params["timeInForce"] = "GTC"

    elif order_type == "STOP":
        # Stop-Limit order
        params["price"] = validated["price"]           # limit price
        params["stopPrice"] = validated["stop_price"]  # trigger price
        params["timeInForce"] = "GTC"

    elif order_type == "STOP_MARKET":
        params["stopPrice"] = validated["stop_price"]

    return params


def place_order(client: BinanceClient, validated: dict) -> dict:
    """Place an order and return the response."""
    params = build_order_params(validated)

    logger.info(f"Placing order with params: {params}")
    print("\n📋 Order Request Summary:")
    print(f"   Symbol     : {params['symbol']}")
    print(f"   Side       : {params['side']}")
    print(f"   Type       : {params['type']}")
    print(f"   Quantity   : {params['quantity']}")
    if "price" in params:
        print(f"   Price      : {params['price']}")
    if "stopPrice" in params:
        print(f"   Stop Price : {params['stopPrice']}")
    if "timeInForce" in params:
        print(f"   TimeInForce: {params['timeInForce']}")

    response = client.place_order(params)
    return response


def display_response(response: dict):
    """Pretty-print the order response."""
    print("\n✅ Order Placed Successfully!")
    print("─" * 40)
    print(f"   Order ID    : {response.get('orderId', 'N/A')}")
    print(f"   Symbol      : {response.get('symbol', 'N/A')}")
    print(f"   Status      : {response.get('status', 'N/A')}")
    print(f"   Side        : {response.get('side', 'N/A')}")
    print(f"   Type        : {response.get('type', 'N/A')}")
    print(f"   Orig Qty    : {response.get('origQty', 'N/A')}")
    print(f"   Executed Qty: {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice", "0")
    if avg_price and avg_price != "0":
        print(f"   Avg Price   : {avg_price}")

    price = response.get("price", "0")
    if price and price != "0":
        print(f"   Price       : {price}")

    stop_price = response.get("stopPrice", "0")
    if stop_price and stop_price != "0":
        print(f"   Stop Price  : {stop_price}")

    print(f"   Time In Force: {response.get('timeInForce', 'N/A')}")
    print("─" * 40)
    logger.info(f"Order response: {response}")
