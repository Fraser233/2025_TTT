#!/usr/bin/env python
# Author: Fengze Yang <fred.yang@utah.edu>
# Date: 2025-03-28

"""
Example how to connect to a Ouster Gemini Detect TCP stream. Assumes that the object_list
is streaming on port 3302, and that the heartbeat is set to
"heartbeat_message": "{\"heartbeat\": [{}]}".
"""

import json
import socket
import ssl

from typing import Callable

# User defined variables. This is currently configured to listen to port
# 3302, which is by default is the `object_list` data.
HOST = "10.206.12.168"
PORT = 3302

# Ouster Gemini Detect defined variables
ENDIAN_TYPE = "big"
FRAME_SIZE_B = 4
ADDRESS = (HOST, PORT)


def recv(socket_client: ssl.SSLContext, num_bytes: int) -> bytearray:
    """
    Helper Function to recv n bytes or return an empty byte array if EOF is
    hit.

    Args:
        socket_client (ssl.SSLSocket): The socket connected to the TCP
        stream.
        num_bytes (int): The number of bytes to receive

    Returns:
        bytearray: The read bytes from the socket. Empty bytearray on
        timeout or connection reset.
    """
    data = bytearray()

    # It is possible only part of the message is read. We loop until we
    # received the whole message
    while len(data) < num_bytes:
        remaining_bytes = num_bytes - len(data)
        try:
            packet = socket_client.recv(remaining_bytes)

        # If the socket times out or is reset, no data could be received.
        except (socket.timeout, ConnectionResetError):
            return bytearray()

        # Append the data
        data.extend(packet)

    return data


def read_frames(
    socket_client: ssl.SSLContext, callback_function: Callable, *args: tuple
) -> None:
    """
    Indefinitely reads in frames of data. The first 4 bytes of the message is
    expected to be the size of the message, and then that size will be read
    immediately afterwards. Repeats until connection is lost.

    Args:
        socket_client (ssl.SSLSocket): The socket connected to the TCP
        stream.
        callback_function (Callable): The callback function to call when
        receiving a valid set of data. The first parameter must be the
        JSON from the TCP stream, and the remaining arguments will be passed
        through args.
        args (tuple): The remaining arguments of the callback_function.
    """
    while True:
        # Gets the size of the frame
        frame_size_b = recv(socket_client, FRAME_SIZE_B)

        # If the size is different than expected, we didn't receive a response.
        # Return None, signalling either a failure to read the message, or that
        # there were no present objects
        if len(frame_size_b) == 0:
            return

        # Convert the byte data to an integer, representing the number of bytes
        # of the message. Then read that size of data from the stream
        frame_size = int.from_bytes(frame_size_b, ENDIAN_TYPE)
        data = recv(socket_client, frame_size)

        # Received no data, return None
        if len(data) == 0:
            return

        data = json.loads(data.decode("utf-8"))

        # If the dictionary contains "heartbeat" as a key, the message was a
        # heartbeat. Continue to the next message. Note that this is
        # configurable using the LidarHub settings.
        if "heartbeat" in data.keys():
            continue

        callback_function(data, *args)


# Create the ssl context
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
ssl_context.verify_mode = ssl.CERT_NONE
# Create the socket client
socket_client = ssl_context.wrap_socket(socket.create_connection(ADDRESS))

# This reads the frame data indefinitely. The first parameter is the socket.
# The next parameter is the callback function to pass the JSON data to.
# Additional parameters can be passed to be passed onto the function. The
# following line currently passes the JSON data to the print function. The
# following line can be updated with a custom callback function
read_frames(socket_client, print)

# Close the socket connection
socket_client.close()
