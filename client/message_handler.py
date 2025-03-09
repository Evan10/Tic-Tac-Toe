import asyncio
from common.utils import (
    prepare_socket_message,
    reconstruct_socket_message,
    validate_message,
)
import common.message_types as mt


class message_handler:

    def __init__(self):

        self.reader = None
        self.writer = None
        self.connected_to_server = False

        self._message_in_queue = []
        self._message_out_queue = []
        pass

    def init_IO(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.connected_to_server = True

    def is_IO_inited(self):
        return self.connected_to_server

    def close(self):
        self.connected_to_server = False

    @staticmethod
    def check_message_type(message, message_type):
        return message.get(mt.MESSAGE_TYPE, None) == message_type

    async def recieve_messages(self):
        while self.connected_to_server:
            try:
                rcv = await self.reader.readuntil(mt.MESSAGE_SEPARATOR.encode())
            except asyncio.IncompleteReadError:
                print("Socket disconnected")
                return
            try:
                obj = reconstruct_socket_message(rcv)
                print(f"Message from Server:{obj}")
            except:
                raise ValueError("Invalid json")
            if obj[mt.MESSAGE_TYPE] == mt.KICK:
                self.close()
            self._message_in_queue.append(obj)

    def get_messages(self, count=-1):
        if count < 0:
            messages = self._message_in_queue.copy()
            self._message_in_queue.clear()
            return messages
        else:
            msgs = []
            for i in range(min(count, len(self._message_in_queue))):
                msgs.append(self._message_in_queue.pop(0))
            return msgs

    async def _flush_messages(self):
        while len(self._message_out_queue) > 0:
            message = self._message_out_queue.pop(0)
            msg_bytes = prepare_socket_message(message)
            print(f"Message Being Sent {message}")
            self.writer.write(msg_bytes)
            await self.writer.drain()
            print("message sent")

    async def _on_disconnect(self):
        disconnect_msg = {mt.MESSAGE_TYPE: mt.CLOSE_SESSION}
        self.add_to_queue(disconnect_msg)
        await self._flush_messages()

    async def send_messages(self):
        while self.connected_to_server:
            if len(self._message_out_queue) > 0:
                await self._flush_messages()
            else:
                await asyncio.sleep(1)
        await self._on_disconnect()

    def add_to_queue(self, obj):
        try:
            validate_message(obj)
            self._message_out_queue.append(obj)
            print("message validated")
        except ValueError as e:
            print(f"An invalid message to server was created, \n {e.args}")
