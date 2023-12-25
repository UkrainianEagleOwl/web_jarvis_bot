import aiohttp
import asyncio
import platform
import logging
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError
import names
from datetime import datetime, timedelta
import aiofiles

logging.basicConfig(level=logging.INFO)


async def get_exchange_rates(date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?date={date}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception if the response status is not 2xx
                result = await response.json()
                return result
        except aiohttp.ClientError as e:
            logging.error(f"An error occurred during the request: {e}")
            return None


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)  # Renamed method name
        except WebSocketProtocolError as err:
            logging.error(err)
        finally:
            await self.unregister(ws)

    async def do_exchange_command(self, message, ws: WebSocketServerProtocol):
        await ws.send(f"{ws.name}: {message}")
        try:
            if message == "exchange":
                num_days = 1
            else:
                split_msg = message.split()  # Extract the number of days
                if len(split_msg) > 1:
                    num_days = int(split_msg[1])
                else:
                    num_days = 1
            if 1 <= num_days <= 10:
                today = datetime.now()
                exchange_rate_data = list()
                for days_ago in range(num_days, 0, -1):
                    target_date = today - timedelta(days=days_ago)
                    formatted_date = target_date.strftime("%d.%m.%Y")
                    exchange_rates = await get_exchange_rates(formatted_date)
                    if exchange_rates is not None:
                        day_rates = list()
                        for rate in exchange_rates.get("exchangeRate", []):
                            currency = rate["currency"]
                            if currency in [
                                "USD",
                                "EUR",
                            ]:  # Filter EUR and USD currencies
                                sale_rate = rate.get("saleRate", rate["saleRateNB"])
                                purchase_rate = rate.get(
                                    "purchaseRate", rate["purchaseRateNB"]
                                )
                                rate_info = f"{currency} sale - {sale_rate}, purchase - {purchase_rate}"
                                day_rates.append(rate_info)

                        day_data = f"{formatted_date}: {' | '.join(day_rates) } |\n"
                        exchange_rate_data.append(day_data)
                await ws.send(
                    f"Exchange rates for the last {num_days} days:\n{' | '.join(exchange_rate_data)}"
                )
            else:
                await ws.send(
                    "Invalid number of days. Please provide a value between 1 and 10."
                )
        except ValueError:
            await ws.send("Invalid input. Please provide a valid number of days.")

    async def distribute(self, ws: WebSocketServerProtocol):  # Renamed method name
        async for message in ws:
            if message.startswith("exchange"):
                self.do_exchange_command(message, ws)
            else:
                await ws.send(f"{ws.name}: {message}")

    async def write_to_file(self, name, num_days):
        try:
            async with aiofiles.open("exchange_log.txt", "a") as f:
                await f.write(
                    f"{name} executed the exchange command for the last {num_days} days\n"
                )
        except Exception as file_error:
            logging.error(f"Error writing to file: {file_error}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, "localhost", 8080):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
