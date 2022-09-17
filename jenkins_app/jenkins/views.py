import os

import firebase_admin
import requests
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from firebase_admin import credentials
from rest_framework.views import APIView

from jenkins.models import Developer
from jenkins.version import d,BUILD_URL

from .build_info import create_build_info
from .models import PushNotification
from .push_notification import start_notifications

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

firebase_cred = credentials.Certificate(
    BASE_DIR+"/jenkins/mfteambuild-firebase-adminsdk-m2lom-e5e1a39810.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)


class CreateUser(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            jenkins_username = request.data.get('jenkins_username')
            build_token = request.data.get('build_token')
            Developer.objects.create(username=username, password=make_password(
                password), jenkins_username=jenkins_username, build_token=build_token)
        except Exception as e:
            print(e)
            data = {'error': "Error in creating User"}
            return JsonResponse(data=data, status=400)
        return JsonResponse(data={'success': "User Created Successfully"}, status=200)


class LoginUser(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            a = Developer.objects.filter(username=username).first()
            if a and check_password(password, a.password):
                data = {'username': a.username,
                        'jenkins_username': a.jenkins_username, 'build_token': a.build_token}
                return JsonResponse(data=data, status=200)
            else:
                return JsonResponse(data={'error': 'username or password incorrect'}, status=400)

        except Exception as e:
            print(e)
            return JsonResponse(data={'error': 'Error in getting response'}, status=500)

    def get(self, request):
        return JsonResponse(data={'success': "ok"}, status=200)


class VersionInfo(APIView):
    def get(self, request):
        return JsonResponse(data=d, status=200, safe=False)


class StartBuild(APIView):
    def post(self, request):
        started_build = []
        try:
            print(request.data['build_data'])
            username = request.data['username']
            a = Developer.objects.filter(username=username).first()
            jenkins_username = a.jenkins_username
            build_token = a.build_token
            build_data = eval(request.data['build_data'].replace(
                't', 'T').replace('f', 'F'))
            valueall = build_data[0]
            serverqa = build_data[5]
            server = 'QA' if serverqa else 'UAT'
            avail_build = get_current_build(
                server, jenkins_username, build_token)
            print(avail_build)
            if valueall:
                for i in range(1, 5):
                    if i in avail_build:
                        continue
                    if (server == 'QA' and i == 3):
                        continue
                    resp_code = build_start(
                        jenkins_username, build_token, server, i)
                    if resp_code == 201:
                        started_build.append(i)
            else:
                for i in range(1, 5):
                    if i in avail_build or (server == 'QA' and i == 3):
                        continue
                    elif build_data[i]:
                        resp_code = build_start(
                            jenkins_username, build_token, server, i)
                        if resp_code == 201:
                            started_build.append(i)
            data = {'started_build': started_build,
                    'already_going': avail_build}
            print(data)
            return JsonResponse(data=data, status=200)
        except Exception as e:
            print(e)
            data = {'error': 'error in getting data for server'}
            return JsonResponse(data=data, status=400)
        # print(response.status_code)


class Build_Current_Info(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            print(username)
            a = Developer.objects.filter(username=username).first()
            # time.sleep(10)
            build_data = create_build_info().call_jenkins(a.jenkins_username, a.build_token)
            # build_data = {
            #     'current_build': [],
            #     'mfapplication': [{
            #         'is_building': True,
            #         'server': 'QA',
            #         'user': 'chetanghadawaje',
            #         'build_result': 'None',
            #         'build_time': '2022-09-02 00:40:22',
            #         'estimatedDuration': 282,
            #         'build_estimate': 1,
            #         'percent_value': 32
            #     }],
            #     'mfadmin': [{
            #         'is_building': False,
            #         'server': 'UAT',
            #         'user': 'rushikeshbhavsar',
            #         'build_result': 'SUCCESS',
            #         'build_time': '2022-08-30 18:32:32',
            #         'estimatedDuration': 248,
            #         'build_estimate': 1,
            #         'percent_value': 0
            #     }],
            #     'mfcronicle': [{
            #         'is_building': False,
            #         'server': 'QA',
            #         'user': 'shivanjalikadam',
            #         'build_result': 'SUCCESS',
            #         'build_time': '2022-09-01 19:15:43',
            #         'estimatedDuration': 75,
            #         'build_estimate': 1,
            #         'percent_value': 0
            #     }],
            #     'mfconsumer': [{
            #         'is_building': False,
            #         'server': 'UAT',
            #         'user': 'mayurkulkarni',
            #         'build_result': 'None',
            #         'build_time': '2022-09-01 21:01:45',
            #         'estimatedDuration': 263,
            #         'build_estimate': 3,
            #         'percent_value': 90
            #     }]
            # }
            print(build_data)
            return JsonResponse(data=build_data, status=200)
        except Exception as e:
            print(e)
            build_data = {"error": "error in getting data"}
            return JsonResponse(data=build_data, status=400)


def build_start(username, build_token, server, service_name):
    # time.sleep(10)
    if server == 'QA' and service_name == 2:
        server = 'NPQ'
    elif server == 'UAT' and service_name == 2:
        server = 'NPU'
    params = {
        'ENVIRONMENT': server,
    }
    url = BUILD_URL[service_name]
    response = requests.post(url, params=params, auth=(username, build_token))
    # print(url)
    return response.status_code
    # return 201


def get_current_build(server, user, token):
    build_data = create_build_info().call_jenkins(user, token)
    # build_data = {
    #     'current_build':[{'mfadmin':'QA','user':'vishal'},{'mfapplication':'QA','user':'vishal'}]
    # }
    avail_build = []
    current_build = build_data.get('current_build')
    for i in current_build:
        if i.get('mfapplication', None) and i['mfapplication'] == server:
            avail_build.append(1)
        if i.get('mfcronicle', None) and i['mfcronicle'] == server:
            avail_build.append(2)
        if i.get('mfadmin', None) and i['mfadmin'] == server:
            avail_build.append(3)
        if i.get('mfconsumer', None) and i['mfconsumer'] == server:
            avail_build.append(4)
    return avail_build


class pushNotifcations(APIView):
    def post(self, request):
        try:
            print(request.data)
            username = request.data.get('username')
            token = request.data.get('token')
            print(token)
            dev = Developer.objects.get(username=username)
            obj, created = PushNotification.objects.update_or_create(
                developer=dev, notification_token=token)
            # response = messaging.subscribe_to_topic(token, 'mf_team')
            # print(response.success_count, 'tokens were subscribed successfully')
        except Exception as e:
            print(e)
            data = {"error": "Error in service"}
            return JsonResponse(data=data, status=400)
        return JsonResponse(data={"success": "Entry Created"}, status=200)
