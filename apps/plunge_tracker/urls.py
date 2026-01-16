from django.urls import path
from apps.plunge_tracker import views

app_name = 'plunge_tracker'

urlpatterns = [
    path('', views.plunge_list, name='plunge_list'),
    path('api/weather/', views.get_weather_data, name='get_weather_data'),
]
