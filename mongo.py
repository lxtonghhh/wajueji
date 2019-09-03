# -*- coding: utf-8 -*-
import sys
import pymongo
import random
import logging

MONGODB_CONFIG = {
    'host': '112.74.160.190',
    'port': 27017,
    'username': None,
    'password': None,
    'dbname': 'share'
}


class MongoConn(object):
    def __init__(self, config):
        try:
            host = config['host']
            port = config['port']
            username = config['username']
            password = config['password']
            self.conn = pymongo.MongoClient(host, port)
            self.db = self.conn[config['dbname']]
        except Exception:
            logging.error("######Connect statics fail")
            sys.exit(1)
        logging.warning("######DB: {0} connect successfully!".format(config['dbname']))

    def close(self):
        self.conn.close()

    def get_coll(self, collname):
        coll = self.db[collname]
        if coll:
            return coll
        else:
            # print('Coll: %s not found' % collname)
            logging.error('Coll: %s not established' % collname)
            return None


if __name__ == '__main__':
    myconn = MongoConn(config=MONGODB_CONFIG)
    coll = myconn.get_coll("wx_uid_coll")
    print(coll)
    count = coll.find().count()
    print(count)
