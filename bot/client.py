"""
client.py - Binance Futures Testnet API client wrapper
"""

import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from bot.logging_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })

    def _get_server_time(self) -> int:
        """Fetch Binance server time to avoid clock skew errors."""
        try:
            resp = self.session.get(BASE_URL + "/fapi/v1/time", timeout=5)
            return resp.json()["serverTime"]
        except Exception:
            return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        """Add timestamp and HMAC-SHA256 signature to params."""
        params["timestamp"] = self._get_server_time()
        params["recvWindow"] = 10000
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, endpoint: str, params: dict = None, signed: bool = True):
        """Make an HTTP request to Binance Futures Testnet."""
        url = BASE_URL + endpoint
        params = params or {}
        if signed:
            params = self._sign(params)

        logger.info(f"REQUEST {method.upper()} {url} | params: {self._sanitize(params)}")

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            logger.info(f"RESPONSE {response.status_code} | {response.text[:500]}")
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Network error: {e}")
            raise ConnectionError(f"Could not reach Binance Testnet. Check your internet connection.\n{e}")
        except requests.exceptions.Timeout:
            logger.error("Request timed out.")
            raise TimeoutError("Request to Binance Testnet timed out.")
        except requests.exceptions.HTTPError as e:
            error_body = {}
            try:
                error_body = response.json()
            except Exception:
                pass
            logger.error(f"HTTP error {response.status_code}: {error_body}")
            msg = error_body.get("msg", str(e))
            raise RuntimeError(f"Binance API error [{response.status_code}]: {msg}")

    def _sanitize(self, params: dict) -> dict:
        """Remove sensitive info from logs."""
        return {k: ("***" if k == "signature" else v) for k, v in params.items()}

    def get_exchange_info(self, symbol: str) -> dict:
        """Fetch exchange info for a symbol."""
        return self._request("GET", "/fapi/v1/exchangeInfo", {"symbol": symbol}, signed=False)

    def get_account(self) -> dict:
        """Fetch account info."""
        return self._request("GET", "/fapi/v2/account")

    def place_order(self, params: dict) -> dict:
        """Place a new order on Binance Futures Testnet."""
        return self._request("POST", "/fapi/v1/order", params)

    def get_order(self, symbol: str, order_id: int) -> dict:
        """Get status of an existing order."""
        return self._request("GET", "/fapi/v1/order", {"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an existing order."""
        return self._request("DELETE", "/fapi/v1/order", {"symbol": symbol, "orderId": order_id})
