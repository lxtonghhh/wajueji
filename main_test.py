from fetchers.TechIndex import scan_share
from task.fetch_share_tick import start
from utils.process import daemonize
from sender import send_message
from utils.common import get_args

if __name__ == "__main__":
    args = get_args()

    if len(args) == 0:
        send_message(subject="推荐-" + "超卖", content=[], attachments=[])
    else:
        if args[0] == "s":
            scan_share(is_test=True)
        elif args[0] == "f":
            start()
        elif args[0] == "r":
            send_message(subject="推荐-" + "超卖", content=[], attachments=[])

