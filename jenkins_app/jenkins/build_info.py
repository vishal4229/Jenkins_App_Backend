
import datetime
import time
from datetime import timedelta

import requests

from jenkins.version import SERVER_URLS, JOB_NAMES


class CreateJobsBuildData():
    """
    Generate all jobs Build related Data by calling Jenkins api
    """    

    def __init__(self,username,build_token):
        self.username = username
        self.build_token = build_token
        
    def call_jenkins(self):
        """_summary_
            Generate data containing all job current status and additional information
        Returns:
            _type_: dict
        """        
        data = {'current_build': []}
        if self.username and self.build_token:
            for index, url in enumerate(SERVER_URLS):
                data[JOB_NAMES[index]] = []
                success,initial_response = self.jenkins_response(url)
                if success:
                    self.build_related_calcution(data, index, initial_response)
                    if initial_response['nextBuild']:
                        self.next_build(data, index, url, initial_response)
                    if initial_response['previousBuild']:
                        self.previous_build(data, index, url, initial_response)
        return data

    def previous_build(self,data, index, url, resp):
        """_summary_
            Checks the Previous Build Status from Jenkins Queue
        Args:
            data (_type_): Common dict for whole data entry
            index (_type_): current index of server list
            url (_type_): server url
            resp (_type_): initial response from jenkins
        """        
        url = url.replace('lastBuild', str(
                        resp['previousBuild']['number']))
        success,response = self.jenkins_response(url)
        if success and response['building']:
            self.build_related_calcution(
                            data, index, response)

    def next_build(self,data, index, url, resp):
        """_summary_
            Checks the Next Build Status from Jenkins Queue
        Args:
            data (_type_): Common dict for whole data entry
            index (_type_): current index of server list
            url (_type_): server url
            resp (_type_): initial response from jenkins
        """
        url = url.replace('lastBuild', str(
                        resp['nextBuild']['number']))
        success,response = self.jenkins_response(url)
        if success and response['building']:
            self.build_related_calcution(
                            data,index, response)
                

    def jenkins_response(self,url):
        """_summary_
            Call jenkins Job specific Api and returns repsonse
        Args:
            url (_type_): Jenkins Job server URL

        Returns:
            _type_: Success return bool depending on jenkins response
        """        
        success = False
        response = requests.post(url, auth=(self.username,self. build_token))
        if response.status_code in (200,299):
            response = response.json()
            success = True
        else:
            response = response.text()
        return success,response

    def build_related_calcution(self, data, index, response):
        """_summary_
            All the Calculations related to Build,percentage,estimates is done here.
        Args:
            data (_type_): Common dict for whole data entry
            index (_type_): current index of server list
            response (_type_): initial response from jenkins

        Returns:
            _type_: Dict
        """     
        build_estimate = 3
        is_building = response['building']
        server = response['actions'][0]['parameters'][0]['value'] if index == 2 else response['actions'][0]['parameters'][2]['value']
        if server == 'NPQ':
            server == 'QA'
        elif server == 'NPU':
            server = 'UAT'
        user = response['actions'][1]['causes'][0]['userId']
        build_result = str(response['result'])
        build_time, build_time_datetime = self.decode_build_time(response)
        estimatedDuration = int(response['estimatedDuration']/1000)
        if is_building == True:
            data['current_build'].append(
                {JOB_NAMES[index]: server, 'user': user})
            build_estimate,percent_value = self.calculate_percent_value(
                build_time_datetime, estimatedDuration)
        else:
            percent_value = 0
        #Create Final Response Dictionary
        data[JOB_NAMES[index]].append({
            'is_building': is_building,
            'server': server,
            'user': user,
            'build_result': build_result,
            'build_time': str(datetime.datetime.strptime(build_time, '%Y-%m-%d %H:%M:%S')+timedelta(hours=5.5)),
            'estimatedDuration': estimatedDuration,
            'build_estimate': build_estimate,
            'percent_value': percent_value
        })
        return data

    def calculate_percent_value(self, build_time_datetime, estimatedDuration):
        total_second = max(0, (datetime.datetime.now() -
                               build_time_datetime).total_seconds())
        build_estimate = 3
        if total_second >= estimatedDuration:
            percent_value = 99
        else:
            percent_value = max(0, int(total_second/estimatedDuration*100))
            build_estimate = min(
                (estimatedDuration-total_second)/(100-percent_value), 5)
        return build_estimate,percent_value

    def decode_build_time(self, response):
        build_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(int(str(response['timestamp'])[:-3])))
        build_time = datetime.datetime.strptime(
            build_time, '%Y-%m-%d %H:%M:%S')
        build_time_datetime = build_time - timedelta(minutes=7.8)
        # print('*'*10,build_time_datetime,response['timestamp'],datetime.datetime.now())
        build_time = datetime.datetime.strftime(
            build_time_datetime, '%Y-%m-%d %H:%M:%S')

        return build_time, build_time_datetime
