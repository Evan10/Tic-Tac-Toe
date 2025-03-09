from server.player_handler import player_handler
from server.server_commandline import server_command_line_commands
from common.utils import (
    create_id,
    prepare_socket_message,
    reconstruct_socket_message,
    validate_message,
)
from common import message_types as mt
from server.matchmaker import game_queue
from server.game_instance import game_instance
from server.player import player
import asyncio
import json
import logging


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    plyr_hndlr: player_handler,
    matchmaker,
):
    logging.info("Client Connected")
    player_id = create_id()
    username = None
    logging.debug(f"ID generated for client {player_id}")

    while username is None:
        message = await reader.readuntil(mt.MESSAGE_SEPARATOR.encode())
        try:
            obj = reconstruct_socket_message(message)
            logging.debug(f"message:{message}")
            if validate_message(obj, mt.CLIENT_INFO):
                username = obj[mt.USERNAME]
            elif validate_message(obj, mt.CLOSE_SESSION):
                logging.info("User disconnected before choosing a username")
                return
            else:
                logging.warning("Invalid username")
        except (TypeError, ValueError) as e:
            logging.warning(f"Invalid username message: {e.args}")

    logging.info(f"Username {username} accepted")

    new_player = player(username, player_id, reader, writer, matchmaker)

    plyr_hndlr.add_player(player_id, new_player)
    try:
        io_tasks = new_player.init_IO()
        await io_tasks
    except Exception as e:
        logging.error(e)


async def server_loop(mtch_mkr: game_queue, plyer_hndlr: player_handler):
    while True:
        mtch_mkr.update()
        plyer_hndlr.update()
        await asyncio.sleep(1)


SERVER_LOCATION = "server_location"
PORT = "port"
CONFIG_FILE = "common/server_config.json"

def load_config_data():
    with open(CONFIG_FILE, "r") as config_file:
        file = config_file.read()
        config_obj = json.loads(file)
        return config_obj


async def main():

    logging.basicConfig(level=logging.DEBUG)

    plyr_hndlr = player_handler()
    mtch_mkr = game_queue()

    server_config = load_config_data()

    server_socket = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, plyr_hndlr, mtch_mkr),
        server_config[SERVER_LOCATION],
        server_config[PORT],
    )

    server_info = server_socket.sockets[0].getsockname()
    server_task = asyncio.create_task(server_socket.serve_forever())
    loop_task = asyncio.create_task(server_loop(mtch_mkr, plyr_hndlr))

    async def close_server(reason="Server Close"):
        mtch_mkr.force_quit_all_games()
        await plyr_hndlr.kick_all_players(reason)
        loop_task.cancel()
        server_socket.close()
        logging.info("Server closed")

    commands_task = asyncio.create_task(
        server_command_line_commands(plyr_hndlr, mtch_mkr, close_server)
    )

    logging.info(f"Server started on {server_info[0]}. Listening on port {server_info[1]}")
    try:
        await asyncio.gather(commands_task, server_task, loop_task)
    except asyncio.CancelledError:
        logging.info("Closing server gracefully")

    logging.info("Server Closed")


if __name__ == "__main__":
    asyncio.run(main())
