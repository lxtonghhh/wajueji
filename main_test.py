from fetchers.TechIndex import scan_share
from utils.process import daemonize

if __name__ == "__main__":
    scan_share(is_test=True)
