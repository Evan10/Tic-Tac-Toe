import asyncio
import json
import logging
import server.matchmaker as matchmaker
from common.utils import (
    prepare_socket_message,
    reconstruct_socket_message,
    validate_message,
)
from server.game_instance import game_instance
from common import message_types as mt


class player:

    def __init__(self, name, id, reader, writer, game_queue: matchmaker.game_queue):
        self.name = name
        self.id = id

        self.in_game = False
        self.current_game: game_instance = None
        self.team = None  # "X" | "O" | None

        self.connected = True
        self.add_to_client_queue = None

        self.game_queue = game_queue

        self.streams = (reader, writer)
        self._flush_queue = None
        self.tasks = None
        pass

    def disconnected(self):
        self.connected = False
        self.quit_game_queue()
        if self.tasks is not None:
            for task in self.tasks:
                task.cancel()
        logging.info(f"Player {self.name} disconnected")

    async def _kick_player(self, reason="Unknown reason"):
        self.game_queue.remove_player_from_queue(self)
        if self.add_to_client_queue is not None:
            kick_msg = {mt.MESSAGE_TYPE: mt.KICK, mt.REASON: reason}
            self.add_to_client_queue(kick_msg)
        self.connected = False
        if self._flush_queue is not None:
            await self._flush_queue()
        logging.info(f"Player {self.name} kicked for {reason}")
        if self.tasks is not None:
            for task in self.tasks:
                task.cancel()

    def join_game_queue(self):
        self.game_queue.add_player_to_queue(self)

    def quit_game_queue(self):
        if self.game_queue.is_player_in_queue(self):
            self.game_queue.remove_player_from_queue(self)

    async def init_IO(self):
        reader, writer = self.streams
        add_to_queue, send_messages, flush_messages = self.message_writer_handler(
            writer
        )
        self._flush_queue = flush_messages
        self.add_to_client_queue = add_to_queue
        recieve_messages = self.message_reader_handler(reader)
        wrt_task = asyncio.create_task(send_messages())
        rd_tsk = asyncio.create_task(recieve_messages())
        self.tasks = (rd_tsk, wrt_task)
        self.send_connect_message()
        await asyncio.gather(wrt_task, rd_tsk)

    def send_connect_message(self):
        return_message = {
            mt.MESSAGE_TYPE: mt.START_SESSION,
            mt.ID: str(self.id),
            mt.USERNAME: self.name,
        }
        self.add_to_client_queue(return_message)

    def message_reader_handler(self, reader: asyncio.StreamReader):

        async def recieve_messages():
            while self.connected:
                try:
                    rcv = await reader.readuntil(mt.MESSAGE_SEPARATOR.encode())
                    obj = None
                except asyncio.IncompleteReadError:
                    logging.warning(f"Player: {str(self)}  socket closed")
                    self.disconnected()
                    return
                try:
                    obj = reconstruct_socket_message(rcv)
                    logging.debug(f"Message from client: {obj}")
                except:
                    logging.error(f'Invalid Json "{obj!s}" recieved')
                message_executor(obj)
            logging.info("Reader finished")

        def message_executor(obj):
            if validate_message(obj):
                if obj[mt.MESSAGE_TYPE] == mt.CLOSE_SESSION:
                    self.disconnected()
                if self.current_game != None:
                    self.current_game.from_player(obj, self.id)
                elif obj[mt.MESSAGE_TYPE] == mt.JOIN_QUEUE:
                    self.join_game_queue()
                elif obj[mt.MESSAGE_TYPE] == mt.QUIT_QUEUE:
                    self.quit_game_queue()
            else:
                logging.error('Invalid message "{obj}" recieved')

        return recieve_messages

    def message_writer_handler(self, writer: asyncio.StreamWriter):

        message_out_queue = []

        async def flush_messages():
            while len(message_out_queue) > 0:
                message: str = message_out_queue.pop(0)
                logging.debug(f"Message Being Sent {message}")
                msg_bytes = prepare_socket_message(message)
                writer.write(msg_bytes)
                await writer.drain()
                logging.debug("Message sent")

        async def send_messages():
            while self.connected:
                if len(message_out_queue) > 0:
                    await flush_messages()
                else:
                    await asyncio.sleep(1)
            logging.info("Writer finished")

        def add_to_queue(obj):
            try:
                validate_message(obj)
                message_out_queue.append(obj)
                logging.debug("Message added to message queue")
            except ValueError:
                logging.error('Invalid message "{obj}" atempted to be sent')

        return add_to_queue, send_messages, flush_messages

    def __str__(self):
        return f"username:{self.name}, id:{self.id}, in game: {self.in_game}, connected: {self.connected}"
