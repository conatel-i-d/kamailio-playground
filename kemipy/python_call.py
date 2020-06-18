import re
import KSR

from utils import ksr_print
from Kamailio import Kamailio

CONTACT_HEADER_REGEX = "(?P<prefix>[^;]+).*app-id=(?P<app_id>[^;]+).*pn-type=(?P<pn_type>[^;]+).*pn-tok=(?P<pn_tok>[^;]+);pn-silent=(?P<pn_silent>[^;]+);(?P<suffix>.*)"

def mod_init():
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

    def parse_contact_header(self, msg):
        try:
            match = re.search(CONTACT_HEADER_REGEX, KSR.pv.get("$ct"))
            if getattr(match, 'group', None) is None:
                return 1
            app_id = match.group("app_id")
            pn_type = match.group("pn_type")
            pn_token = match.group("pn_tok")
            prefix = match.group("prefix")
            suffix = match.group("suffix")
            KSR.hdr.remove("Contact");
            KSR.hdr.append("Contact: " + ';'.join([prefix, suffix]) + "\r\n");
        except Exception as e:
            KSR.info(str(e))
        return 1
