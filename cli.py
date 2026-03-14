"""
cli.py - CLI entry point for the Binance Futures Testnet Trading Bot

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
  python cli.py --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 2000
  python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stop-price 79000 --price 78500
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.orders import place_order, display_response
from bot.validators import validate_all
from bot.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="🤖 Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  Market BUY:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

  Limit SELL:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000

  Stop-Market BUY:
    python cli.py --symbol ETHUSDT --side BUY --type STOP_MARKET --quantity 0.01 --stop-price 2000

  Stop-Limit SELL:
    python cli.py --symbol BTCUSDT --side SELL --type STOP --quantity 0.001 --stop-price 79000 --price 78500
        """,
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol (e.g., BTCUSDT)")
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"], help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP"],
        help="Order type: MARKET, LIMIT, STOP_MARKET, or STOP (stop-limit)",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity (e.g., 0.001)")
    parser.add_argument(
        "--price",
        default=None,
        help="Limit price — required for LIMIT and STOP orders",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        default=None,
        help="Stop trigger price — required for STOP_MARKET and STOP orders",
    )
    return parser.parse_args()


def load_credentials():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n❌ ERROR: BINANCE_API_KEY and BINANCE_API_SECRET must be set in a .env file.\n"
            "  Create a .env file in the project root:\n"
            "    BINANCE_API_KEY=your_key_here\n"
            "    BINANCE_API_SECRET=your_secret_here\n"
        )
        logger.error("API credentials not found in environment.")
        sys.exit(1)

    return api_key, api_secret


def main():
    args = parse_args()

    print("\n🚀 Binance Futures Testnet Trading Bot")
    print("=" * 45)

    # Load credentials
    api_key, api_secret = load_credentials()

    # Validate inputs
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
        logger.info(f"Validated inputs: {validated}")
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)

    # Initialize client
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    # Place order
    try:
        response = place_order(client, validated)
        display_response(response)
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except (ConnectionError, TimeoutError) as e:
        print(f"\n❌ Network Error: {e}")
        logger.error(f"Network error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ API Error: {e}")
        logger.error(f"API error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
