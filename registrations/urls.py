from django.urls import path

from . import views


urlpatterns = [
    path('health/', views.health, name='health'),
    path('register/', views.register, name='register'),
    path('newsletter/', views.newsletter, name='newsletter'),
]
