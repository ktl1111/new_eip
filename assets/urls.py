from django.urls import path
from assets import views

urlpatterns = [
    path('', views.index, name='index')
]