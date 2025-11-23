from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Certifications and Courses
    path('certification/<int:pk>/', views.certification_detail, name='certification_detail'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('module/<int:pk>/', views.module_view, name='module_view'),

    # AJAX Progress Tracking
    path('module/<int:pk>/complete/', views.mark_module_complete, name='mark_module_complete'),
    path('module/<int:pk>/video-progress/', views.update_video_progress, name='update_video_progress'),

    # Certificate Downloads
    path('certificate/course/<int:pk>/download/', views.download_course_certificate, name='download_course_certificate'),
    path('certificate/professional/<int:pk>/download/', views.download_professional_certificate, name='download_professional_certificate'),
]
