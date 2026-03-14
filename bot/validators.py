"""
validators.py - Input validation for trading bot CLI arguments
"""

from bot.logging_config import get_logger

logger = get_logger(__name__)

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET", "STOP"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValueError(f"Invalid symbol '{symbol}'. Must be alphanumeric (e.g., BTCUSDT).")
    logger.debug(f"Symbol validated: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    logger.debug(f"Side validated: {side}")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    logger.debug(f"Order type validated: {order_type}")
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}")
    logger.debug(f"Quantity validated: {qty}")
    return qty


def validate_price(price: str) -> float:
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}")
    logger.debug(f"Price validated: {p}")
    return p


def validate_stop_price(stop_price: str) -> float:
    """Validate stop price for STOP/STOP_MARKET orders."""
    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than 0. Got: {sp}")
    logger.debug(f"Stop price validated: {sp}")
    return sp


def validate_all(symbol, side, order_type, quantity, price=None, stop_price=None):
    """
    Run all relevant validations and return a clean dict of validated values.
    Raises ValueError with a clear message on any failure.
    """
    validated = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValueError("Price is required for LIMIT orders.")
        validated["price"] = validate_price(price)

    if order_type.upper() in ("STOP", "STOP_MARKET"):
        if stop_price is None:
            raise ValueError("Stop price (--stop-price) is required for STOP/STOP_MARKET orders.")
        validated["stop_price"] = validate_stop_price(stop_price)
        if order_type.upper() == "STOP":
            if price is None:
                raise ValueError("Price (limit price) is required for STOP (stop-limit) orders.")
            validated["price"] = validate_price(price)

    return validated
