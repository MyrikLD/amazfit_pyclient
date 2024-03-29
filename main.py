import argparse
import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from bleak import BleakClient

from chanked_decoder import ChunkedDecoder
from chanked_encoder import ChunkedEncoder
from fetch.fetch_activity.data_fetcher import FetchActivity
from handlers.auth_handler import AuthHandler
from handlers.battery_handler import BatteryClient
from handlers.connection_handler import ConnectionClient
from handlers.heartrate_handler import HeartRateClient
from handlers.http_handler import HttpClient
from handlers.logs_handler import LogsClient
from handlers.steps_handler import StepsClient

CHARACTERISTIC_HR = UUID("00002a37-0000-1000-8000-00805f9b34fb")


def print_chars(client: BleakClient):
    for service in client.services:
        print(f"{service.uuid}: {service.description}")
        for char in service.characteristics:
            print(f"\t{char.uuid}: {char.description}")


async def main(address: str, key: str):
    disconnect_event = asyncio.Event()
    async with BleakClient(
        address,
        disconnected_callback=lambda x: disconnect_event.set(),
        timeout=30,
    ) as client:
        decoder = ChunkedDecoder(client)
        encoder = ChunkedEncoder(client)

        eh = AuthHandler(key, encoder, decoder)
        http = HttpClient(encoder, decoder)
        hr = HeartRateClient(encoder, decoder)
        steps = StepsClient(encoder, decoder)
        conn = ConnectionClient(encoder, decoder)
        logs = LogsClient(encoder, decoder)
        battery = BatteryClient(encoder, decoder)

        await decoder.start_notify()
        await eh.autenticate()

        await steps.get_steps()
        await conn.get_mtu()

        # print_chars(client)

        await notify_hr(client)

        await FetchActivity(client).start(
            since=datetime.now().astimezone() - timedelta(days=1),
        )

        await disconnect_event.wait()
        print("Disconnected")


async def notify_hr(client):
    def heart_rate(char, data: bytearray):
        print(f"Heart rate: {int.from_bytes(data)}")

    heart_rate_measurement_char = client.services.get_characteristic(CHARACTERISTIC_HR)
    await client.start_notify(heart_rate_measurement_char, heart_rate)


if __name__ == "__main__":
    logging.getLogger("bleak").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="Python amazfit client")

    parser.add_argument(
        "-a",
        "--address",
        required=True,
        help="Bluetooth address",
    )

    parser.add_argument(
        "-k",
        "--key",
        required=True,
        help="Bluetooth key",
    )

    args = parser.parse_args()

    asyncio.run(main(address=args.address, key=args.key))
