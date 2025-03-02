from django.urls import path
from .views import *

urlpatterns = [
    # home
    path('', Index.as_view(), name='index'),
    path('search/', Search.as_view(), name='search'),
    path('send-email/', SendEmail.as_view(), name='send_email'),

    # course
    path('course/<int:pk>/', CourseDetail.as_view(), name='course_detail'),
    path('course/<int:pk>/update/', UpdateCourse.as_view(), name='updateCourse'),
    path('course/<int:pk>/delete/', DeleteCourse.as_view(), name='deleteCourse'),
    path('course/add/', AddCourse.as_view(), name='addCourse'),

    # student
    path('student/<int:pk>/', StudentDetail.as_view(), name='student_detail'),

    # auth
    path('auth/register/', Register.as_view(), name='register'),
    path('auth/login/', Login.as_view(), name='login'),
    path('auth/logout/', Logout.as_view(), name='logout'),

    # not found
    path('not-found/', NotFound.as_view(), name='not_found'),

    # profile
    path('profile/<str:username>', Profile.as_view(), name='profile'),

    # settings
    path('settings/', Settings.as_view(), name='settings'),
    path('settings/personal-data/update/', Settings.as_view(), name='personal_data'),
    path('settings/personal-data/photo/delete', Settings.as_view(), name='delete_photo'),
    path('settings/password/change/', Settings.as_view(), name='change_password'),
]
