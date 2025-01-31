from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page , name='login'),
    path('signup/', views.signup_page , name='signup'),
    path('dashboard/', views.dashboard_page , name='dashboard'),
    path('logout/', views.logout_page , name='logout'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]
