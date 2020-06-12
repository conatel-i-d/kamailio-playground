# Kamailio configuration class.
# It must have at least the `ksr_request_route` method defined.
# If not, Kamailio will throw an error.

import KSR as KSR
from utils import ksr_print

PBX_IP = '192.168.22.56'
PBX_PORT = '5060'

class Kamailio:
    def __init__(self):
        ksr_print('Kamailio.__init__')

    def child_init(self, rank):
        ksr_print(f'kamailio.child_init({str(rank)})')
        return 0
    
    # SIP request routing
    def ksr_request_route(self, msg):
        ksr_print('Kamailio.ksr_request_route')
        KSR.rtpproxy.rtpproxy_manage('iewc')
        KSR.tm.t_relay(PBX_IP, PBX_PORT)
        return 1;

    def ksr_onsend_route(self, msg):
        ksr_print('Kamailio.ksr_onsend_route')
        return 1

    def ksr_on_reply_route(self, msg):
        ksr_print('Kamailio.ksr_on_reply_route')
        if has_body("application/sdp"):
            KSR.rtpproxy.rtpproxy_manage("iewc")
        return 1
