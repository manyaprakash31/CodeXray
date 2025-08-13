from django.urls import path
from . import views
from .views import logout_view
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
]
