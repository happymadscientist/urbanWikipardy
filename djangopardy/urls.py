from django.urls import path

from . import views

urlpatterns = [
	path('randomCategory', views.randomCategory),
	path('commands/<str:sessionId>/<str:teamName>', views.getCommands),
	path('category/<str:sessionId>', views.postCategory),
	path('login/<str:loginType>', views.login),
	path('command/<str:sessionId>/<str:teamName>', views.postCommand),
]