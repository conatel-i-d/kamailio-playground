from utils import ksr_print
from Kamailio import Kamailio

def mod_init():
    ksr_print('From python mod init')
    return Kamailio()


class Kamailio:
    def __init__(self):
        ksr_print('Kamailio.__init__')

    def child_init(self, rank):
        ksr_print(f'kamailio.child_init({str(rank)})')
        return 0
    
    def ksr_request_route(self, msg):
        ksr_print('Kamailio.ksr_request_route')
        return 1;

    def ksr_on_reply_route(self, msg):
        ksr_print('Kamailio.ksr_on_reply_route')
        return 1

    def something(self, msg, message):
        ksr_print(f"something: {message}")
        return 1
