from django.contrib import admin
from django.urls import path
from jenkins.views import CreateUser,LoginUser,VersionInfo,Build_Current_Info,StartBuild,pushNotifcations

urlpatterns = [
    path('create_user/', CreateUser.as_view()),
    path('login/', LoginUser.as_view()),
    path('version_info/', VersionInfo.as_view()),
    path('build_info/', Build_Current_Info.as_view()),
    path('start_build/', StartBuild.as_view()),
    path('create_token/',pushNotifcations.as_view()),
]
