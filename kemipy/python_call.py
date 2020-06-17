import json

import requests

from utils import ksr_print
from Kamailio import Kamailio

SERVER_TOKEN = 'AAAAD6-7oYY:APA91bGmQIuVgvwPgytrlaC1Cq3QytUu7LFHHSfYVONCl4vXjUoNM7Ap_lE5IvdrU-fK92Hq9-RFFrUm5oI7gETR8qZO3rRDdD8fYX__OQrbGAxZdNZMa-T-XLbAbcW_YjgicXbWOdRq'

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
        #response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        #ksr_print(json.dumps(response.json(), indent=4, sort_keys=True))
        return 1
