from django.urls import path
from django.contrib import admin

from . import views
from .views import *

urlpatterns = [
	path('admin/', admin.site.urls),
	path('register/', views.register, name='register'),
	path('', login, name='login'),
	path('main/', main, name='main'),
	path("catalog/", catalog, name = "catalog"),
	path("search/", search, name = "search"),
	path("sell_hub/", sell_hub, name = "sell_hub"),
 	path('logout/', views.logout_view, name='logout'),

	# main components req 1
	path("add/", add, name = "add"),
	path("edit/<pk>/", edit, name = "edit"),
	path("delete/<pk>/", delete, name = "delete"),
	path("buy/<pk>/", buy, name = "buy"),
]