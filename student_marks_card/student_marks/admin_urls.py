from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views
from .decorators import is_admin

app_name = 'custom_admin'

urlpatterns = [
    path('dashboard/', login_required(user_passes_test(is_admin)(views.admin_dashboard)), name='admin_dashboard'),
    path('create-user/', login_required(user_passes_test(is_admin)(views.create_user)), name='create_user'),
    path('import-data/', login_required(user_passes_test(is_admin)(views.import_data)), name='import_data'),
    path('execute-sql-query/', login_required(user_passes_test(is_admin)(views.execute_sql_query)), name='execute_sql_query'),
    path('visualize-data/', login_required(user_passes_test(is_admin)(views.visualize_data)), name='visualize_data'),
    path('enter-marks/', login_required(user_passes_test(is_admin)(views.enter_marks)), name='enter_marks'),
    path('manage-students/', login_required(user_passes_test(is_admin)(views.manage_students)), name='manage_students'),
    path('manage-teachers/', login_required(user_passes_test(is_admin)(views.manage_teachers)), name='manage_teachers'),
    path('manage-subjects/', login_required(user_passes_test(is_admin)(views.manage_subjects)), name='manage_subjects'),
    path('manage-classes/', login_required(user_passes_test(is_admin)(views.manage_classes)), name='manage_classes'),
    path('manage-courses/', login_required(user_passes_test(is_admin)(views.manage_courses)), name='manage_courses'),
    path('manage-sessions/', login_required(user_passes_test(is_admin)(views.manage_sessions)), name='manage_sessions'),
    path('manage-exam-dates/', login_required(user_passes_test(is_admin)(views.manage_exam_dates)), name='manage_exam_dates'),
    path('manage-marks/', login_required(user_passes_test(is_admin)(views.manage_marks)), name='manage_marks'),
    path('view-marks/', login_required(user_passes_test(is_admin)(views.view_marks)), name='view_marks'),
    path('get-student-classes/', login_required(user_passes_test(is_admin)(views.get_student_classes)), name='get_student_classes'),
    path('get-courses/', login_required(user_passes_test(is_admin)(views.get_courses)), name='get_courses'),
] 