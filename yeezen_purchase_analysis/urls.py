from django.urls import path
from yeezen_purchase_analysis import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download, name="download")
]