import os, re, traceback, json
from pathlib import Path
import KSR

from dotenv import load_dotenv

load_dotenv(verbose=True, dotenv_path=Path('/etc/kamailio/.env'))

from exceptions import UndefinedEnvironmentVariable
from firebase_push_notifications import FirebasePushNotifications

CONTACT_HEADER_REGEX = "(?P<prefix>[^;]+).*app-id=(?P<app_id>[^;]+).*pn-type=(?P<pn_type>[^;]+).*pn-tok=(?P<pn_tok>[^;]+);pn-silent=(?P<pn_silent>[^;]+);(?P<suffix>.*)"
USERNAME_REGEX = ".*sip:(?P<username>[^@]+).*"
FIREBASE_LEGACY_API_URL = "https://fcm.googleapis.com/fcm/send"

def mod_init():
    return Kamailio()

class Kamailio:
    def __init__(self):
        try:
            self.pn = FirebasePushNotifications()
        except UndefinedEnvironmentVariable as e:
            KSR.error(e.message)
        except:
            KSR.info(traceback.format_exc())

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
        result = dict()
        result["app_id"] = match.group("app_id")
        result["pn_type"] = match.group("pn_type")
        result["pn_token"] = match.group("pn_tok")
        result["prefix"] = match.group("prefix")
        result["suffix"] = match.group("suffix")
        match = re.search(USERNAME_REGEX, result["prefix"])
        if getattr(match, "group", None) is None:
            return None
        result["username"] = match.group("username")
        return result

    def update_contact_header(self, value):
        KSR.hdr.remove("Contact");
        KSR.hdr.append("Contact: " + value + "\r\n");

    def extract_contact(self, msg):
        KSR.info(">>> Extract contact")
        try:
            result = self.parse_contact(KSR.pv.get("$ct"))
            if result is None:
                return 1
            contact = ";".join([result["prefix"], result["suffix"]])
            self.update_contact_header(contact)
            self.pn.update_pn_contact(result["username"], 
                app_id=result["app_id"],
                pn_type=result["pn_type"],
                pn_token=result["pn_token"],
            )
        except:
            KSR.info(traceback.format_exc())
        return 1

    def send_push_notification(self, msg):
        KSR.info(">>> Send push notification")
        try:
            self.pn.send_push_notification(KSR.pv.get("$tU"),
                call_id=KSR.pv.get("$ci"),
                sip_from=KSR.pv.get("$fU"),
                loc_key=KSR.pv.get("$mi"),
                loc_args=KSR.pv.get("$oU")
            )
        except:
            KSR.info(traceback.format_exc())
        return 1