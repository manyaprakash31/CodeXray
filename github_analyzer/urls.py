from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_input_view, name="profile_input"),
    path('repos/', views.repo_list_view, name="repo_list"),
    path("analyze/<str:username>/<str:repo_name>/<path:file_path>/", views.analyze_file_view, name="analyze_file"),
    path("chatbot/", views.chatbot_view, name="chatbot_view"),
    path("repo/<str:repo_name>/", views.repo_chatbot_view, name="repo_chatbot_view"),
    path("history/", views.user_history_view, name="user_history"),
    path("history/<int:pk>/", views.view_analysis_detail, name="view_analysis_detail"),
    path("download/<int:history_id>/", views.download_pdf_view, name="download_pdf"),
    path("profile/", views.profile_input_view, name="user_profile"),
]
