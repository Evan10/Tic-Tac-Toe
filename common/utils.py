import json
import logging
import re
import time
from types import NoneType
from uuid import UUID, uuid1

import common.message_types as mt


REGEX_PARTITION_PATTERN = rf"{mt.MESSAGE_SEPARATOR}"
PARTITION_REPLACEMENT = f"{mt.MESSAGE_SEPARATOR[0:2]}//{mt.MESSAGE_SEPARATOR[2:]}"


def prepare_socket_message(obj) -> bytes:
    if isinstance(obj, (NoneType, str)):
        raise TypeError("Invalid Type")
    obj_str = json.dumps(obj)

    # if the Partition str is found in the  obj's string change it to stop it from messing up the message
    obj_str: str = re.sub(REGEX_PARTITION_PATTERN, PARTITION_REPLACEMENT, obj_str)
    obj_str += mt.MESSAGE_SEPARATOR
    logging.debug(f"Prepared message: {obj_str}")
    return obj_str.encode()


def reconstruct_socket_message(obj_bytes: bytes | bytearray):
    if isinstance(obj_bytes, NoneType):
        raise TypeError("Invalid Type")
    obj_str: str = obj_bytes.decode()
    # restore the message to its original state
    obj_str = re.sub(REGEX_PARTITION_PATTERN, "", obj_str)
    obj_str = re.sub(PARTITION_REPLACEMENT, REGEX_PARTITION_PATTERN, obj_str)
    logging.debug(f"Reconstructed message: {obj_str}")
    obj = json.loads(obj_str)
    return obj


def validate_message(obj: dict | str, expected_type=None):
    if obj is None:
        return False
    if isinstance(obj, str) and obj == "":
        return True
    obj_type = obj.get(mt.MESSAGE_TYPE)
    if obj_type == None:
        raise ValueError("Invalid message type")
    if expected_type is not None and expected_type != obj_type:
        return False
    expected_entries: list = mt.MESSAGE_DATA[obj_type]
    for entry in expected_entries:
        if obj.get(entry) is None:
            raise ValueError(f"Invalid message, missing entry: {entry}")
    return True


def create_id():
    return str(uuid1())


ID_REGEX = r"^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$"

def is_id(string: str):
    if not isinstance(string, (str, UUID)):
        raise ValueError(f"Expected a string but recieved {type(string)}")
    return re.search(ID_REGEX, string) is not None


def get_current_time():
    return time.strftime("%H:%M:%S")
