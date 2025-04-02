from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('import-data/', views.import_data, name='import_data'),
    path('view-marks/', views.view_marks, name='view_marks'),
    path('visualize-data/', views.visualize_data, name='visualize_data'),
    path('execute-sql-query/', views.execute_sql_query, name='execute_sql_query'),
    path('', views.index, name='index'),
]