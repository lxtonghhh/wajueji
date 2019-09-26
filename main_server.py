#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
from fetchers.TechIndex import scan_share
from task.fetch_share_tick import start
from utils.process import daemonize
from sender import send_message
from utils.common import get_args, get_exception_info, str2bytes,bytes2str
import time, sys, traceback
import zmq


def run_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        try:
            #  Wait for next request from client
            message = bytes2str(socket.recv())
            # print("Received request: %s" % message)
            if message == "e":
                socket.send(b"error")
                raise Exception("错误测试")
            elif message == "t":
                send_message(subject="系统状态测试", content=["邮件发送正常"], attachments=[])
                socket.send(str2bytes(message + " -->finished"))
            elif message == "s":
                send_message(subject="系统状态报告", content=["开始扫描"], attachments=[])
                socket.send(str2bytes(message + " -->start"))
                scan_share(is_test=False)
            else:
                send_message(subject="系统状态报告", content=["运行正常"], attachments=[])
                socket.send(str2bytes(message + " -->finished"))

        except Exception as e:
            print(get_exception_info(e))
            send_message(subject="系统错误报告", content=[get_exception_info(e)], attachments=[])



def main():
    args = get_args()

    if len(args) == 0:
        run_server()
    elif args[0] == "d":
        daemonize(func=run_server)


if __name__ == "__main__":
    main()
