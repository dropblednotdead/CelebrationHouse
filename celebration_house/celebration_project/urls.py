from django.urls import path, include
from celebration_project import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('search', views.search, name='search'),
    path('seat', views.seat, name='seat'),
]