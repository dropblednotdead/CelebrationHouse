from django.urls import path, include
from celebration_project import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('search', views.search, name='search'),
    path('seat', views.seat, name='seat'),
    path('booking', views.booking, name='booking'),
    path('authorization/', views.AuthorizationUser.as_view(), name='authorization'),
    path('registration/', views.RegistrationUser.as_view(), name='registration'),
    path('profile/', views.user_profile_view, name='profile'),
    path('logout_user/', views.logout_user, name='logout'),
    path('admin', views.booking_edit, name='admin'),
]