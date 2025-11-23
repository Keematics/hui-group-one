from django.urls import path
from . import views

urlpatterns = [
    # =====================================
    # AUTHENTICATION
    # =====================================
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # =====================================
    # MAIN PAGES
    # =====================================
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # =====================================
    # USER PROFILE MANAGEMENT
    # =====================================
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # =====================================
    # ENROLLMENTS
    # =====================================
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('certification/<int:pk>/enroll/', views.enroll_certification, name='enroll_certification'),
    path('certification/<int:pk>/unenroll/', views.unenroll_certification, name='unenroll_certification'),

    # =====================================
    # CERTIFICATIONS AND COURSES (Learner View)
    # =====================================
    path('certification/<int:pk>/', views.certification_detail, name='certification_detail'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('module/<int:pk>/', views.module_view, name='module_view'),

    # =====================================
    # AJAX PROGRESS TRACKING
    # =====================================
    path('module/<int:pk>/complete/', views.mark_module_complete, name='mark_module_complete'),
    path('module/<int:pk>/video-progress/', views.update_video_progress, name='update_video_progress'),

    # =====================================
    # CERTIFICATE DOWNLOADS
    # =====================================
    path('certificate/course/<int:pk>/download/', views.download_course_certificate, name='download_course_certificate'),
    path('certificate/professional/<int:pk>/download/', views.download_professional_certificate, name='download_professional_certificate'),

    # =====================================
    # INSTRUCTOR: DASHBOARD
    # =====================================
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),

    # =====================================
    # INSTRUCTOR: CERTIFICATION MANAGEMENT
    # =====================================
    path('instructor/certification/create/', views.create_certification, name='create_certification'),
    path('instructor/certification/<int:pk>/edit/', views.edit_certification, name='edit_certification'),
    path('instructor/certification/<int:pk>/delete/', views.delete_certification, name='delete_certification'),

    # =====================================
    # INSTRUCTOR: COURSE MANAGEMENT
    # =====================================
    path('instructor/course/create/', views.create_course, name='create_course'),
    path('instructor/course/create/<int:certification_pk>/', views.create_course, name='create_course_for_cert'),
    path('instructor/course/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('instructor/course/<int:pk>/delete/', views.delete_course, name='delete_course'),

    # =====================================
    # INSTRUCTOR: MODULE MANAGEMENT
    # =====================================
    path('instructor/course/<int:course_pk>/module/create/', views.create_module, name='create_module'),
    path('instructor/module/<int:pk>/edit/', views.edit_module, name='edit_module'),
    path('instructor/module/<int:pk>/delete/', views.delete_module, name='delete_module'),
]
