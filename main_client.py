#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
from fetchers.TechIndex import scan_share
from task.fetch_share_tick import start
from utils.process import daemonize
from sender import send_message
from utils.common import get_args, get_exception_info, str2bytes, bytes2str
import time, sys, traceback
import zmq


def prepare(host):
    context = zmq.Context()

    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://{0}:5555".format(host))
    return socket


def run_client(host="localhost"):
    socket = prepare(host)
    #  Do 10 requests, waiting each time for a response
    while True:
        command = input("-->输入指令：")
        print("->即将执行指令", command)
        socket.send(str2bytes(command))
        message = socket.recv()
        print("->指令执行结果", bytes2str(message))


def main(host="localhost"):
    args = get_args()

    if len(args) == 0:
        run_client(host)
    elif args[0] == "d":
        pass


TX_HOST = "132.232.62.227"
HOST_IN_USE = TX_HOST
if __name__ == "__main__":
    main(host=HOST_IN_USE)
