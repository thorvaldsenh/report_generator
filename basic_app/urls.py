from django.urls import path
from . import views

app_name = 'basic_app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    # path('basic_app/menu/',views.menu,name='menu'),



]
