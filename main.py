import argparse
import asyncio
import logging
from asyncio import sleep
from uuid import UUID

from bleak import BleakClient

from chanked_decoder import ChunkedDecoder
from chanked_encoder import ChunkedEncoder
from handlers.auth_handler import EncryptionHandler
from handlers.connection_handler import ConnectionClient
from handlers.heartrate_handler import HeartRateClient
from handlers.http_handler import HttpClient
from handlers.logs_handler import LogsClient
from handlers.steps_handler import StepsClient

CHARACTERISTIC_HR = UUID("00002a37-0000-1000-8000-00805f9b34fb")


async def main(address: str, key: str):
    async with BleakClient(
        address,
        disconnected_callback=lambda x: print("Disconnected!"),
    ) as client:
        decoder = ChunkedDecoder(client)
        encoder = ChunkedEncoder(client)

        eh = EncryptionHandler(key, encoder, decoder)
        decoder.add_handler(eh)

        http = HttpClient(encoder, decoder)
        decoder.add_handler(http)

        hr = HeartRateClient(encoder, decoder)
        decoder.add_handler(hr)

        steps = StepsClient(encoder, decoder)
        decoder.add_handler(steps)

        conn = ConnectionClient(encoder, decoder)
        decoder.add_handler(conn)

        logs = LogsClient(encoder, decoder)
        decoder.add_handler(logs)

        await decoder.start_notify()
        await eh.autenticate()

        for service in client.services:
            print(f"{service.uuid}: {service.description}")
            for char in service.characteristics:
                print(f"\t{char.uuid}: {char.description}")

        await notify_hr(client)

        print("sleep")
        while 1:
            await sleep(1)


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
