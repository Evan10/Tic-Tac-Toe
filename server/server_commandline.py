from server.player_handler import player_handler
from server.game_instance import game_instance
from common.utils import is_id
from server.player import player
from server.matchmaker import game_queue
import asyncio
import logging
import server.server_commands as sc


def check_args(args, expected_args):
    max = len(expected_args)
    min = len([a for a in expected_args if not a.startswith("_")])
    logging.debug(f"args: {len(args)} min: {min} max: {max}")
    return max >= len(args) and len(args) >= min


def print_help_message():
    msg = f"""Here is a list of commands you can use: 
Kick a player using: {sc.KICK_PLAYER!s}
Get a players id using: {sc.GET_PLAYER_ID!s}
Quit a specific game using: {sc.QUIT_GAME!s}
Close the server using: {sc.QUIT_SERVER!s}
See this message using: {sc.HELP!s}
Get player list using: {sc.GET_PLAYER_LIST!s}
Get game list using: {sc.GET_GAME_LIST!s}
Get player queue using: {sc.GET_PLAYER_QUEUE!s}
If an argument has an underscore at the begining \"_\" it is optional\n"""
    logging.info(msg)


def quit_game_given_game_id(mtch_mkr: game_queue, args):
    mtch_mkr.force_quit_game(args[0])


async def server_command_line_commands(
    plyr_hndlr: player_handler, mtch_mkr: game_queue, close_server
):
    running = True
    while running:
        clc = await asyncio.to_thread(input, "")
        cmd = clc.split(" ")
        cmd_type = cmd[0].lower()
        args = cmd[1:]
        args_num = len(args)
        if cmd_type == sc.KICK_PLAYER[sc.CMD]:
            if not check_args(args, sc.KICK_PLAYER[sc.ARGS]):
                message = f"Invalid command, expected 1-2 arguments in this format {sc.KICK_PLAYER!s} but got {args_num} argument(s)"
                logging.warning(message)
                continue
            await plyr_hndlr.kick_player_given_identifier(args)
        elif cmd_type == sc.GET_PLAYER_ID[sc.CMD]:
            if not check_args(args, sc.GET_PLAYER_ID[sc.ARGS]):
                message = f"Invalid command, expected 1 arguments in this format {sc.GET_PLAYER_ID!s} but got {args_num} argument(s)"
                logging.warning(message)
                continue
            plyr_hndlr.get_id_given_username(args[0])
        elif cmd_type == sc.HELP[sc.CMD]:
            print_help_message()
        elif cmd_type == sc.QUIT_GAME[sc.CMD]:
            if not check_args(args, sc.QUIT_GAME[sc.ARGS]):
                message = f"Invalid command, expected 1 arguments in this format {sc.QUIT_GAME!s} but got {args_num} argument(s)"
                logging.warning(message)
                continue
            quit_game_given_game_id(mtch_mkr, args)
        elif cmd_type == sc.QUIT_SERVER[sc.CMD]:
            if not check_args(args, sc.QUIT_SERVER[sc.ARGS]):
                message = f"Invalid command, expected 0-1 arguments in this format {sc.QUIT_SERVER!s} but got {args_num} argument(s)"
                logging.warning(message)
                continue
            running = False
            if args_num == 0:
                await close_server()
            else:
                await close_server(args[0])
        elif cmd_type == sc.GET_PLAYER_LIST[sc.CMD]:
            logging.info(plyr_hndlr.get_player_list_str())
        elif cmd_type == sc.GET_GAME_LIST[sc.CMD]:
            logging.info(mtch_mkr.game_list_str())
        elif cmd_type == sc.GET_PLAYER_QUEUE[sc.CMD]:
            logging.info(mtch_mkr.player_queue_list_str())
        else:
            logging.warning(
                f'Invalid command {cmd_type} passed in, type "help" to see valid commands'
            )
    logging.info("Commandline task ending")
