from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import is_admin, is_teacher, is_student

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin URLs
    path('custom-admin/', include('student_marks.admin_urls', namespace='custom_admin')),
    
    # Teacher URLs
    path('teacher/', include('student_marks.teacher_urls', namespace='teacher')),
    
    # Student URLs
    path('student/', include('student_marks.student_urls', namespace='student')),
    
    # Power BI API
    path('api/power-bi-data/', views.power_bi_data, name='power_bi_data'),
]