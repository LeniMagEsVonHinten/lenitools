#!/usr/bin/env python3
# <> with ❤ by @LeniMagEsVonHinten

""" Test command port connection to Maya """

import socket


def send_test_command(host='127.0.0.1', port=4344):
    """ send a test command to a Maya command port """
    address = (host, port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    test_command = 'polyCube()'
    client.send(test_command.encode())
    client.close()
    print("Command: {}".format(test_command))


if __name__ == '__main__':
    send_test_command()
