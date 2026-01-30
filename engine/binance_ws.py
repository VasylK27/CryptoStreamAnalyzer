import asyncio
import json
import websockets

class BinanceWS:
    def __init__(self, symbols):
        """
        :param symbols: list of pairs, for example [“BTCUSDT”, “BTCFDUSD”]
        """
        self.symbols = [s.lower() for s in symbols]
        self.base_url = "wss://stream.binance.com:9443/stream?streams="
        self.is_running = False
        self.latest_data = {}

    def get_url(self):
        streams = "/".join([f"{s}@bookTicker" for s in self.symbols])
        return self.base_url + streams
    
    async def start(self, callback=None):
        """
        Launching the listener. 
        :param callback: function that we will call when receiving new data
        """
        url = self.get_url()
        self.is_running = True

        while self.is_running:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=10) as websocket:
                    print(f"[WS] Connected to Binance: {self.symbols}")
                    while self.is_running:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                            raw_data = json.loads(message)
                            data = raw_data["data"]

                            symbol = data["s"]
                            payload = {
                                "symbol": symbol,
                                "bid": float(data["b"]),
                                "ask": float(data["a"]),
                            }

                            self.latest_data[symbol] = payload

                            if callback:
                                await callback(payload)
                        
                        except asyncio.TimeoutError:
                            continue

            except Exception as e:
                print(f"[WS] Connection error: {e}")
                if self.is_running:
                    print("[WS] Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
            finally:
                print("[WS] Connection closed")

    def stop(self):
        self.is_running = False
