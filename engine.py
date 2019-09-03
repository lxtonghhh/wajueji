from multiprocessing import Process
import os,time
from fetchers.Test import test_meta


if __name__ =="__main__":

    print(os.getpid())
    for i in range(5):
        p= Process(target=test_meta, args=())
        p.start()
