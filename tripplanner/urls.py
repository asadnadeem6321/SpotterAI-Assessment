from django.urls import path
from .views import create_trip_plan, health_check

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('trip-plan/', create_trip_plan, name='trip-plan'),
]
