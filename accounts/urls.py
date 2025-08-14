from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('two-factor/', views.two_factor_view, name='two_factor'),
    path('resend-code/', views.resend_2fa_code, name='resend_2fa_code'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.index),  
]