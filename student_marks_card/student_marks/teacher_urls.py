from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .decorators import is_teacher

app_name = 'teacher'

urlpatterns = [
    path('dashboard/', login_required(views.teacher_dashboard), name='dashboard'),
    path('visualize-data/', login_required(views.visualize_data), name='visualize_data'),
    path('exam-date-marks/', login_required(views.exam_date_marks), name='exam_date_marks'),
    path('students/', login_required(views.teacher_students), name='students'),
    path('student-marks/<str:student_id>/', login_required(views.student_marks), name='student_marks'),
    path('student-analysis/<str:student_id>/', login_required(views.detailed_student_analysis), name='student_analysis'),
] 