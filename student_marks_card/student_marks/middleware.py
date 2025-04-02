from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class CustomAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # List of URLs that don't require authentication
        public_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('index'),
        ]
        
        # Check if the current URL is public
        if request.path in public_urls:
            return None
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('login')
            
        # Check user roles and redirect if necessary
        if request.user.is_superuser:
            admin_urls = [
                reverse('custom_admin:admin_dashboard'),
                reverse('custom_admin:import_data'),
                reverse('custom_admin:manage_students'),
                reverse('custom_admin:manage_teachers'),
                reverse('custom_admin:manage_subjects'),
                reverse('custom_admin:manage_classes'),
                reverse('custom_admin:manage_courses'),
                reverse('custom_admin:manage_sessions'),
                reverse('custom_admin:manage_exam_dates'),
                reverse('custom_admin:manage_marks'),
                reverse('custom_admin:view_marks'),
                reverse('custom_admin:enter_marks'),
            ]
            if request.path not in admin_urls:
                return redirect('custom_admin:admin_dashboard')
                
        elif hasattr(request.user, 'teacher'):
            teacher_urls = [
                reverse('teacher_dashboard'),
                reverse('teacher_students'),
                reverse('teacher_visualize_data'),
                reverse('student_marks', kwargs={'student_id': 'any'}),
            ]
            if request.path not in teacher_urls:
                return redirect('teacher_dashboard')
                
        elif hasattr(request.user, 'student'):
            student_urls = [
                reverse('student_dashboard'),
                reverse('student_marks_view'),
                reverse('student_visualize_data'),
            ]
            if request.path not in student_urls:
                return redirect('student_dashboard')
                
        return None 