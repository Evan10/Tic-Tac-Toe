import asyncio
import json
import threading
from common import message_types as mt
import pygame

from client.message_handler import message_handler
from client.game import game
from client.gui.game_screen import disconnected_screen, username_screen


SERVER_LOCATION = "server_location"
PORT = "port"
CONFIG_FILE = "server_config.json"


def load_config_data():
    with open(CONFIG_FILE, "r") as config_file:
        file = config_file.read()
        config_obj = json.loads(file)
        return config_obj


async def open_server_connection(msg_hndlr: message_handler):
    server_config = load_config_data()

    reader, writer = await asyncio.open_connection(
        server_config[SERVER_LOCATION], server_config[PORT]
    )

    msg_hndlr = msg_hndlr.init_IO(reader, writer)


async def server_connection(msg_hndlr: message_handler):

    await open_server_connection(msg_hndlr)
    print("Client Connected")

    async def start_streams():
        recieve = asyncio.create_task(msg_hndlr.recieve_messages())
        send = asyncio.create_task(msg_hndlr.send_messages())
        await asyncio.gather(send, recieve)

    return start_streams


async def main():

    msg_hndlr = message_handler()

    gm = game(msg_hndlr)

    game_thread = threading.Thread(target=gm.loop)
    game_thread.start()

    try:
        start_streams = await server_connection(msg_hndlr)

        gm.gui_hndlr.switch_screen(username_screen.SCREEN_NAME)
        await start_streams()

    except (ConnectionResetError, ConnectionRefusedError, asyncio.CancelledError) as e:

        dscnnct_scrn: disconnected_screen = gm.gui_hndlr.get_screen(
            disconnected_screen.SCREEN_NAME
        )
        if dscnnct_scrn is not None:
            dscnnct_scrn.set_reason(type(e).__name__)
        gm.gui_hndlr.switch_screen(disconnected_screen.SCREEN_NAME)

    game_thread.join()


if __name__ == "__main__":
    asyncio.run(main())
