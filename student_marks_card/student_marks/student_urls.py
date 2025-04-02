from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .decorators import is_student

app_name = 'student'

urlpatterns = [
    path('dashboard/', login_required(views.student_dashboard), name='dashboard'),
    path('marks/', login_required(views.student_marks_view), name='marks_view'),
    path('visualize-data/', login_required(views.student_visualize_data), name='visualize_data'),
] 