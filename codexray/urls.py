from django.contrib import admin
from django.urls import path, include
from github_analyzer import views as github_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    # 🚀 Landing Page
    path('', github_views.landing_page, name='landing'),

    # 🔍 GitHub Analyzer module
    path('analyze/', include('github_analyzer.urls')),

    # 👤 Auth module (Signup/Login/Logout)
    path('users/', include('users.urls')),

    # 🐞 Bug Detector (Code Debugger module)
    path('bug/', include('bug_detector.urls')),

    # 📜 GitHub Analyzer History
    path("history/", github_views.user_history_view, name="user_history"),
    path('analyze/history/<int:pk>/', github_views.view_analysis_detail, name='analysis_detail'),
]
