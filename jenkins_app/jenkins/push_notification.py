import threading
import requests
import time
import json

from .build_info import CreateJobsBuildData
from .models import PushNotification,Developer
from urllib3.exceptions import InsecureRequestWarning
from jenkins.version import FCM_KEY,USERNAME
# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# dev = Developer.objects.get(username=USERNAME)

def start_notifications():
    while True:
        try:
            msg =''
            time.sleep(60)
            # build_data = CreateJobsBuildData().call_jenkins(dev.jenkins_username, dev.build_token)
            build_data = {
            'current_build':[{'mfadmin':'QA','user':'vishal'},{'mfapplication':'QA','user':'vishal'}]
            }
            current_build = build_data.get('current_build')
            for i in current_build:
                first_key = list(i)[0]
                list_value = list(i.values())
                first_value = list_value[0]
                second_value = list_value[1]
                msg+= f"{first_key}|{first_value}|{second_value}\n"
            send_push_notification(msg)
        except Exception as e:
            print(e)
            pass
                

def send_push_notification(msg):
    url =  "https://fcm.googleapis.com/fcm/send"
    headers = {
        'Authorization': FCM_KEY,
        'Content-Type': 'application/json',
        }
    body = {
        "to":"/topics/mf_team",
        "notification": {"body": msg, "title": "Build Started", "sound": "default",
        "priority":"HIGH",
        }
    }
    requests.post(url=url,headers=headers,data=json.dumps(body),verify=False)
    
timer = threading.Thread(target=start_notifications)
timer.daemon = True
timer.start() 
threading.Thread.__init__.daemon = True