from django.urls import path
from . import views

app_name = "bug_detector"

urlpatterns = [
    path('code-debugger/', views.code_debugger_view, name='code_debugger'),
    path('generate-code/', views.generate_code_view, name='generate_code'),
    path('debug-code/', views.debug_code_view, name='debug_code'),
    path('history/', views.debug_history_view, name='debug_history'),path("auth-required/", views.auth_required_view, name="auth_required"),
    path('history/', views.debug_history_view, name='bug_detector_history'),
]
