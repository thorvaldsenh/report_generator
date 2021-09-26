"""report_generator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.generic import TemplateView
from basic_app import views

urlpatterns = [
    path('basic_app/', include('basic_app.urls')),
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name="index"),
    path('report/',views.report,name='report'),
    path('documentation/',views.documentation,name='documentation'),
    # path('example/',views.example,name='example'),
    # path('top_bottom/',views.top_bottom,name='top_bottom'),
    # path('positions/',views.positions,name='positions'),
    # path('charts/',views.ChartView.as_view(),name='charts'),
    # path('strategy/',views.StrategyView.as_view(),name='strategy'),
    # path('api/data/',views.get_data,name='api-data'),
    # path('api/performance/data/',views.ChartData.as_view(),name='api-performance-data'),
    # path('api/currency/data/',views.CurrencyData.as_view(),name='api-currency-data'),
    # path('api/strategy/data/',views.StrategyData.as_view(),name='api-strategy-data'),
    path('robots.txt', TemplateView.as_view(template_name="basic_app/robots.txt", content_type='text/plain')),


]
