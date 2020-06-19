import os, re, traceback
from pathlib import Path
import KSR

import redis
from dotenv import load_dotenv

from utils import ksr_print
from Kamailio import Kamailio

load_dotenv(verbose=True, dotenv_path=Path('/etc/kamailio/.env'))

FIREBASE_SERVER_KEY = os.environ.get("FIREBASE_SERVER_KEY", "Not found")
CONTACT_HEADER_REGEX = "(?P<prefix>[^;]+).*app-id=(?P<app_id>[^;]+).*pn-type=(?P<pn_type>[^;]+).*pn-tok=(?P<pn_tok>[^;]+);pn-silent=(?P<pn_silent>[^;]+);(?P<suffix>.*)"
USERNAME_REGEX = ".*sip:(?P<username>[^@]+).*"

def mod_init():
    return Kamailio()

class Kamailio:
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379, db=0)
        pass

    def child_init(self, rank):
        return 0
    
    def ksr_request_route(self, msg):
        return 1;

    def ksr_on_reply_route(self, msg):
        return 1

    def parse_contact(self, value):
        match = re.search(CONTACT_HEADER_REGEX, value)
        if getattr(match, "group", None) is None:
            return None
        app_id = match.group("app_id")
        pn_type = match.group("pn_type")
        pn_token = match.group("pn_tok")
        prefix = match.group("prefix")
        suffix = match.group("suffix")
        match = re.search(USERNAME_REGEX, prefix)
        if getattr(match, "group", None) is None:
            return None
        username = match.group("username")
        return dict(
            username=username,
            contact=";".join([prefix, suffix]),
            pn=";".join([app_id,pn_type,pn_token]),
        )

    def update_contact_header(self, value):
        KSR.hdr.remove("Contact");
        KSR.hdr.append("Contact: " + value + "\r\n");

    def extract_contact(self, msg):
        try:
            result = self.parse_contact(KSR.pv.get("$ct"))
            if result is None:
                return 1
            self.update_contact_header(result["contact"])
            self.r.sadd(result["username"], result["pn"])
        except:
            KSR.info(traceback.format_exc())
        return 1

    def send_push_notification(self, msg):
        try:
            KSR.info(KSR.pv.get("$fU"))
            KSR.info(FIREBASE_SERVER_KEY)
            tokens = []
            for token in self.r.smembers(KSR.pv.get("$fU")):
                token = token.decode("utf-8")
                tokens.append(token.split(";"))
            KSR.info(str(tokens))
        except:
            KSR.info(traceback.format_exc())
        return 1