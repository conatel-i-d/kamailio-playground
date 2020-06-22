import os, uuid, json
import KSR
from datetime import datetime

from pyfcm import FCMNotification

from exceptions import UndefinedEnvironmentVariable
from redis_client import create_redis_client

FIREBASE_SERVER_KEY = os.environ.get("FIREBASE_SERVER_KEY", None)

class FirebasePushNotifications():

    def __init__(self):
        if FIREBASE_SERVER_KEY is None:
            raise UndefinedEnvironmentVariable("FIREBASE_SERVER_KEY")
        self.redis_client = create_redis_client()
        self.push_service = FCMNotification(api_key=FIREBASE_SERVER_KEY)

    def create_data_message(self, call_id="", sip_from="", loc_key="", loc_args=""):
        return {
            "uuid": str(uuid.uuid4()),
            "call-id": call_id,
            "sip-from": sip_from,
            "loc-key": loc_key,
            "loc-args": loc_args,
            "send-time": str(datetime.now()),
        }

    def update_pn_contact(self, username, app_id=None, pn_type=None, pn_token=None):
        if app_id is None or pn_type is None or pn_token is None:
            return
        self.redis_client.sadd(username, ";".join([app_id, pn_type, pn_token]))

    def send_push_notification(self, username, call_id=None, sip_from=None, loc_key=None, loc_args=None):
        tokens = []
        for token in self.redis_client.smembers(username):
            [app_id, pn_type, pn_token] = token.decode("utf-8").split(";")
            KSR.info(f">>> username = {username}")
            KSR.info(f">>> app_id = {app_id}")
            KSR.info(f">>> pn_type = {pn_type}")
            KSR.info(f">>> pn_token = {pn_token}")
            data_message = self.create_data_message(call_id=call_id, sip_from=sip_from, loc_key=loc_key, loc_args=loc_args)
            KSR.info(json.dumps(data_message, indent=4, sort_keys=True))
            result = self.push_service.notify_single_device(
                registration_id=pn_token,
                message_title="Incoming call",
                message_body=f"Incoming call from {sip_from}",
                data_message=data_message,
                time_to_live=120,
            )
            KSR.info(json.dumps(result, indent=4, sort_keys=True))
