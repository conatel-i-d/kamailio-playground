from utils import ksr_print
from Kamailio import Kamailio

def mod_init():
    ksr_print('From python mod init')
    return Kamailio()

class Kamailio:
    def __init__(self):
        pass

    def child_init(self, rank):
        return 0
    
    def ksr_request_route(self, msg):
        return 1;

    def ksr_on_reply_route(self, msg):
        return 1

    def something(self, msg, message):
        return 1
