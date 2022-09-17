
from datetime import timedelta
import requests
import os
import time
import datetime
from backports.zoneinfo import ZoneInfo
from version import URL_LIST

class create_build_info():
    def __init__(self):
      self.urls = URL_LIST
      
      self.job_name = ['mfapplication','mfadmin','mfcronicle','mfconsumer']
      
    def call_jenkins(self,username,build_token):
        data = {'current_build':[]}
        cnt = 0
        if username and build_token:
            for index,url in enumerate(self.urls):
                data[self.job_name[index]] = []
                response = requests.post(url, auth=(username, build_token))
                response = response.json()
                build_no = response['number']
                print(build_no,response['nextBuild'],response['previousBuild'])
                self.new_method(data, cnt, index, response)
                if response['nextBuild']:
                    url = url.replace('lastBuild',str(response['nextBuild']['number']))
                    response = requests.post(url, auth=(username, build_token))
                    response = response.json()
                    if response['building']:
                        self.new_method(data, cnt, index, response)
                if response['previousBuild']:
                    url = url.replace('lastBuild',str(response['previousBuild']['number']))
                    response = requests.post(url, auth=(username,build_token))
                    response = response.json()
                    if response['building']:
                        self.new_method(data, cnt, index, response)
        return data

    def new_method(self, data, cnt, index, response):
        is_building = response['building']
        server = response['actions'][0]['parameters'][0]['value'] if index==2 else response['actions'][0]['parameters'][2]['value']
        if server == 'NPQ':
            server = 'QA'
        elif server == 'NPU':
            server = 'UAT'
        user = response['actions'][1]['causes'][0]['userId']
        build_result = str(response['result'])
        build_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(response['timestamp'])[:-3])))
        build_time = datetime.datetime.strptime(build_time,'%Y-%m-%d %H:%M:%S')
        build_time = build_time
        build_time_datetime = build_time - timedelta(minutes=7.8)
        print('*'*10,build_time_datetime,response['timestamp'],datetime.datetime.now())
        build_time = datetime.datetime.strftime(build_time_datetime,'%Y-%m-%d %H:%M:%S')
        estimatedDuration = int(response['estimatedDuration']/1000)
        build_duration = response['duration']
        total_sec = (datetime.datetime.now() - build_time_datetime).total_seconds()
        print(total_sec)
        build_estimate = 1
        if is_building == True:
            data['current_build'].append({self.job_name[index]:server,'user':user})
            # if datetime.datetime.now() < build_time_datetime:
            # build_time_datetime = datetime.datetime.now()
            total_sec = (datetime.datetime.now() - build_time_datetime).total_seconds()
            # print(total_sec)
            if total_sec<0:
                total_sec = 0
            if total_sec >=estimatedDuration:
                percent_value = 99
            else:
                percent_value = int(total_sec/estimatedDuration*100)
                if percent_value <0:
                    percent_value = 0
            cnt+=1
            b1 = (estimatedDuration-total_sec)/(100-percent_value)
            build_estimate = b1 if total_sec < estimatedDuration and b1<5  else 3
        else:
            percent_value = 0
        print(is_building)
        data[self.job_name[index]].append({
            'is_building':is_building,
                'server':server,
                'user':user,
                'build_result':build_result,
                'build_time':str(datetime.datetime.strptime(build_time,'%Y-%m-%d %H:%M:%S')+timedelta(hours=5.5)),
                'estimatedDuration':estimatedDuration,
                'build_estimate':build_estimate,
                'percent_value':percent_value
            })
        return data
    
        
# print(create_build_info().call_jenkins(os.environ['build_username'], os.environ['build_token']))