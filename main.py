from fetchers.TechIndex import scan_share
from utils.process import daemonize

if __name__ == "__main__":
    daemonize(func=scan_share)
