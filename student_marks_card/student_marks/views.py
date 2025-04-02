from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction, connection, models
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import admin
from .models import Session, ExamDate, StudentClass, Course, Student, Teacher, Subject, Marks
from .forms import LoginForm, ImportDataForm, CustomUserCreationForm, StudentRegistrationForm
from .decorators import is_student, is_teacher, is_admin
import pandas as pd
from django.conf import settings
import os
from django.contrib import messages
import matplotlib.pyplot as plt
import io
import base64
import logging
from .visualize_data import (
    subject_wise_analysis,
    student_performance_analysis,
    class_wise_analysis,
    get_top_performers,
    generate_student_report
)
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)

# Define maximum marks for each subject at the top of the file
max_marks = {
    'Physics': 180,
    'Chemistry': 180,
    'Biology': 360
}

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User {user.username} logged in successfully")
            
            # Check user roles and redirect
            if user.is_superuser:
                logger.info(f"User {user.username} is admin, redirecting to admin dashboard")
                return redirect('custom_admin:admin_dashboard')
            elif user.groups.filter(name='Teacher').exists():
                logger.info(f"User {user.username} is teacher, redirecting to teacher dashboard")
                return redirect('teacher:dashboard')
            elif user.groups.filter(name='Student').exists():
                logger.info(f"User {user.username} is student, redirecting to student dashboard")
                return redirect('student:dashboard')
            else:
                logger.warning(f"User {user.username} has no role assigned")
                messages.error(request, 'No role assigned to user')
                return redirect('login')
        else:
            logger.warning(f"Failed login attempt: {form.errors}")
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'student_marks/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = Student.objects.get(user=request.user)
    marks = Marks.objects.filter(student=student).order_by('exam_date', 'subject__name')
    return render(request, 'student_marks/student/view_marks.html', {'marks': marks})

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    # Teacher can see all marks and filter
    sessions = Session.objects.all()
    exam_dates = ExamDate.objects.all().order_by('-date_of_exam')
    courses = Course.objects.all()
    students = Student.objects.all()
    subjects = Subject.objects.all()
    
    # Initialize marks as None
    marks = None
    
    # Only fetch marks if any filter is applied
    session_filter = request.GET.get('session')
    exam_date_filter = request.GET.get('exam_date')
    course_filter = request.GET.get('course')
    student_filter = request.GET.get('student')
    subject_filter = request.GET.get('subject')
    search_term = request.GET.get('search')
    
    # Start with base queryset
    marks = Marks.objects.select_related(
        'student', 'subject', 'student__student_class', 'student__course', 'session', 'exam_date'
    ).order_by('exam_date__date_of_exam', 'student__full_name', 'subject__name')
    
    # Group marks by exam date and student
    grouped_marks = {}
    
    if any([session_filter, exam_date_filter, course_filter, student_filter, subject_filter, search_term]):
        if session_filter:
            marks = marks.filter(session__id=session_filter)
            exam_dates = exam_dates.filter(session_id=session_filter)
            logger.info(f"Applied session filter: {marks.count()} marks")
            
        if exam_date_filter:
            marks = marks.filter(exam_date__id=exam_date_filter)
            logger.info(f"Applied exam date filter: {marks.count()} marks")
            
        if course_filter:
            marks = marks.filter(student__course__id=course_filter)
            logger.info(f"Applied course filter: {marks.count()} marks")
            
        if student_filter:
            marks = marks.filter(student__id=student_filter)
            logger.info(f"Applied student filter: {marks.count()} marks")
            
        if subject_filter:
            marks = marks.filter(subject__id=subject_filter)
            logger.info(f"Applied subject filter: {marks.count()} marks")
            
        if search_term:
            marks = marks.filter(
                Q(student__student_id__icontains=search_term) |
                Q(student__full_name__icontains=search_term)
            )
            logger.info(f"Applied search filter: {marks.count()} marks")
        
        # Group marks by exam date and student
        for mark in marks:
            exam_date = mark.exam_date.date_of_exam
            student_id = mark.student.student_id
            
            if exam_date not in grouped_marks:
                grouped_marks[exam_date] = {}
                
            if student_id not in grouped_marks[exam_date]:
                grouped_marks[exam_date][student_id] = {
                    'student_id': student_id,
                    'full_name': mark.student.full_name,
                    'subjects': {},
                    'total_marks': 0,
                    'max_total': 0
                }
            
            subject_name = mark.subject.name
            max_mark = max_marks.get(subject_name, 100)
            
            grouped_marks[exam_date][student_id]['subjects'][subject_name] = mark.score
            grouped_marks[exam_date][student_id]['total_marks'] += mark.score
            grouped_marks[exam_date][student_id]['max_total'] += max_mark

        # Calculate percentage and sort by total marks
        for exam_date in grouped_marks:
            for student_data in grouped_marks[exam_date].values():
                if student_data['max_total'] > 0:
                    student_data['percentage'] = (student_data['total_marks'] / student_data['max_total']) * 100
                else:
                    student_data['percentage'] = 0

            # Sort students by total marks in descending order
            sorted_students = dict(sorted(
                grouped_marks[exam_date].items(),
                key=lambda x: x[1]['total_marks'],
                reverse=True
            ))
            grouped_marks[exam_date] = sorted_students

    context = {
        'marks': marks,
        'grouped_marks': grouped_marks,
        'sessions': sessions,
        'exam_dates': exam_dates,
        'courses': courses,
        'students': students,
        'subjects': subjects,
        'has_filters': any([session_filter, exam_date_filter, course_filter, student_filter, subject_filter, search_term])
    }
    return render(request, 'student_marks/teacher/view_marks.html', context)

@login_required
@user_passes_test(is_admin)
def import_data(request):
    if request.method == 'POST':
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    excel_file = request.FILES['excel_file']
                    df = pd.read_excel(excel_file)
                    
                    # Get form data
                    course = form.cleaned_data['course']
                    session = form.cleaned_data['session']
                    student_class = form.cleaned_data['student_class']
                    
                    # Process each row
                    for _, row in df.iterrows():
                        # Create or get user
                        user, created = User.objects.get_or_create(
                            username=row['Student_Id'],
                            defaults={
                                'first_name': row['Full_Name'].split()[0],
                                'last_name': ' '.join(row['Full_Name'].split()[1:]) if len(row['Full_Name'].split()) > 1 else ''
                            }
                        )
                        
                        # Create or get student
                        student, created = Student.objects.get_or_create(
                            student_id=row['Student_Id'],
                            defaults={
                                'full_name': row['Full_Name'],
                                'course': course,
                                'session': session,
                                'user': user,
                                'student_class': student_class
                            }
                        )
                        
                        # Create or get exam date
                        exam_date, _ = ExamDate.objects.get_or_create(
                            session=session,
                            course=course,
                            student_class=student_class,
                            date_of_exam=row['Date_of_Exam']
                        )
                        
                        # Process marks for each subject
                        for subject_name in ['Physics', 'Chemistry', 'Biology']:
                            if subject_name in row and pd.notna(row[subject_name]):
                                # Create or get subject
                                subject, _ = Subject.objects.get_or_create(
                                    name=subject_name,
                                    course=course,
                                    student_class=student_class
                                )
                                
                                # Create marks entry
                                Marks.objects.create(
                                    student=student,
                                    subject=subject,
                                    score=row[subject_name],
                                    session=session,
                                    exam_date=exam_date,
                                    course=course,
                                    student_class=student_class
                                )
                    
                    messages.success(request, 'Data imported successfully!')
                    return redirect('custom_admin:import_data')
            except Exception as e:
                messages.error(request, f'Error importing data: {str(e)}')
                logger.error(f"Error importing data: {str(e)}")
    else:
        form = ImportDataForm()
    
    return render(request, 'student_marks/admin/import_data.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    context = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classes': StudentClass.objects.count(),
        'total_courses': Course.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_sessions': Session.objects.count(),
        'total_marks': Marks.objects.count(),
    }
    return render(request, 'student_marks/admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def execute_sql_query(request):
    query = request.GET.get('query', 'SELECT * FROM report.student_marks_marks;')
    results = []
    columns = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        messages.error(request, f"Error executing query: {e}")
        logger.error(f"Error executing query: {e}")

    context = {
        'query': query,
        'results': results,
        'columns': columns,
    }
    return render(request, 'student_marks/admin/execute_sql_query.html', context)

@login_required
def view_marks(request):
    if is_student(request.user):
        return student_dashboard(request)
    elif is_teacher(request.user):
        return teacher_dashboard(request)
    elif is_admin(request.user):
        return admin_dashboard(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def visualize_data(request):
    """Main visualization view that shows all analysis options"""
    try:
        # Get filter values from request
        session_id = request.GET.get('session')
        class_id = request.GET.get('class')
        course_id = request.GET.get('course')
        student_id = request.GET.get('student')
        exam_date = request.GET.get('exam_date')
        
        logger.info(f"Received filter values - Session: {session_id}, Class: {class_id}, Course: {course_id}, Student: {student_id}, Exam Date: {exam_date}")
        
        # Get filter options
        sessions = Session.objects.all().order_by('-session_name')
        classes = StudentClass.objects.all()
        courses = Course.objects.all()
        students = Student.objects.all()
        
        # Start with base exam dates queryset
        exam_dates = ExamDate.objects.all().order_by('-date_of_exam')
        
        # Apply filters to exam dates
        if session_id:
            exam_dates = exam_dates.filter(session_id=session_id)
            logger.info(f"Filtered exam dates for session {session_id}: {exam_dates.count()} dates")
        if class_id:
            exam_dates = exam_dates.filter(student_class_id=class_id)
            logger.info(f"Filtered exam dates for class {class_id}: {exam_dates.count()} dates")
        if course_id:
            exam_dates = exam_dates.filter(course_id=course_id)
            logger.info(f"Filtered exam dates for course {course_id}: {exam_dates.count()} dates")
        
        # Start with base marks queryset and log total marks
        marks = Marks.objects.select_related(
            'student', 'subject', 'student__student_class', 'student__course', 'session', 'exam_date'
        )
        logger.info(f"Total marks before filtering: {marks.count()}")
        
        # Log subject-wise mark counts
        subject_counts = marks.values('subject__name').annotate(
            count=models.Count('id')
        )
        for subject in subject_counts:
            logger.info(f"Marks for {subject['subject__name']}: {subject['count']}")
        
        # Apply filters to marks
        if session_id:
            marks = marks.filter(session_id=session_id)
            logger.info(f"After session filter: {marks.count()} marks")
            
        if class_id:
            marks = marks.filter(student__student_class_id=class_id)
            logger.info(f"After class filter: {marks.count()} marks")
            
        if course_id:
            marks = marks.filter(student__course_id=course_id)
            logger.info(f"After course filter: {marks.count()} marks")
            
        if student_id:
            marks = marks.filter(student_id=student_id)
            logger.info(f"After student filter: {marks.count()} marks")
            
        if exam_date:
            marks = marks.filter(exam_date_id=exam_date)
            logger.info(f"After exam date filter: {marks.count()} marks")
        
        # Prepare data for charts
        subject_data = []
        subject_labels = []
        performance_data = [0, 0, 0, 0]  # [Excellent, Good, Average, Poor]
        
        if marks.exists():
            # Subject-wise average marks in percentage
            subject_averages = marks.values('subject__name').annotate(
                avg_score=models.Avg('score')
            ).order_by('subject__name')
            
            subject_labels = []
            subject_data = []
            
            for item in subject_averages:
                subject_name = item['subject__name']
                avg_score = item['avg_score']
                max_mark = max_marks.get(subject_name, 100)  # Default to 100 if subject not found
                
                # Calculate percentage
                percentage = (avg_score / max_mark) * 100
                
                subject_labels.append(subject_name)
                subject_data.append(round(percentage, 2))
            
            # Performance distribution (using percentages)
            for mark in marks:
                subject_name = mark.subject.name
                max_mark = max_marks.get(subject_name, 100)
                percentage = (mark.score / max_mark) * 100
                
                if percentage >= 85:
                    performance_data[0] += 1  # Excellent
                elif percentage >= 70:
                    performance_data[1] += 1  # Good
                elif percentage >= 50:
                    performance_data[2] += 1  # Average
                else:
                    performance_data[3] += 1  # Poor
        
        context = {
            'sessions': sessions,
            'classes': classes,
            'courses': courses,
            'students': students,
            'exam_dates': exam_dates,
            'subject_labels': subject_labels,
            'subject_data': subject_data,
            'performance_data': performance_data,
            'has_data': marks.exists(),
            'selected_session': session_id,
            'selected_class': class_id,
            'selected_course': course_id,
            'selected_student': student_id,
            'selected_exam_date': exam_date,
        }
        
        return render(request, 'student_marks/teacher/teacher_visualize_data.html', context)
        
    except Exception as e:
        logger.error(f"Error in visualize_data view: {e}", exc_info=True)
        messages.error(request, "एक त्रुटि उत्पन्न हुई। कृपया फिर से कोशिश करें।")
        return redirect('teacher:dashboard')

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def subject_wise_visualization(request):
    """View for subject-wise analysis"""
    marks = Marks.objects.all()
    plot, stats = subject_wise_analysis(marks)
    return JsonResponse({'plot': plot, 'stats': stats})

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def student_performance_visualization(request):
    """View for student performance analysis"""
    marks = Marks.objects.all()
    plot = student_performance_analysis(marks)
    return JsonResponse({'plot': plot})

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def class_wise_visualization(request):
    """View for class-wise analysis"""
    marks = Marks.objects.all()
    plot = class_wise_analysis(marks)
    return JsonResponse({'plot': plot})

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def top_performers_visualization(request):
    """View for top performers analysis"""
    marks = Marks.objects.all()
    subject_toppers, overall_toppers = get_top_performers(marks)
    return JsonResponse({
        'subject_toppers': subject_toppers,
        'overall_toppers': overall_toppers
    })

@login_required
def student_report_visualization(request, student_id):
    """View for individual student report"""
    student = get_object_or_404(Student, id=student_id)
    if not (is_teacher(request.user) or is_admin(request.user) or 
            (is_student(request.user) and request.user == student.user)):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    marks = Marks.objects.filter(student=student)
    plot = generate_student_report(marks)
    return JsonResponse({'plot': plot})

def index(request):
    return render(request, 'index.html')

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def get_student_classes(request):
    """Get student classes for a given session"""
    session_id = request.GET.get('session_id')
    student_classes = []
    if session_id:
        student_classes = list(StudentClass.objects.filter(session_id=session_id).values('id', 'name'))
    return JsonResponse(student_classes, safe=False)

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def get_courses(request):
    """Get courses for a given student class"""
    student_class_id = request.GET.get('student_class_id')
    courses = []
    if student_class_id:
        courses = list(Course.objects.filter(student_class_id=student_class_id).values('id', 'name'))
    return JsonResponse(courses, safe=False)

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def get_subjects(request):
    """Get subjects for a given course"""
    course_id = request.GET.get('course_id')
    subjects = []
    if course_id:
        subjects = list(Subject.objects.filter(course_id=course_id).values('id', 'name'))
    return JsonResponse(subjects, safe=False)

@login_required
@user_passes_test(is_admin)
def create_user(request):
    """View for creating new users with roles"""
    role = request.GET.get('role', 'Teacher')  # Default to Teacher if no role specified
    
    if request.method == 'POST':
        if role == 'Student':
            form = StudentRegistrationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save(commit=False)
                    # Set a default password for students
                    user.set_password('Student@123')  # Default password
                    user.save()
                    messages.success(request, f'Student {user.username} created successfully! Default password: Student@123')
                    return redirect('custom_admin:admin_dashboard')
                except Exception as e:
                    logger.error(f"Error creating student: {e}")
                    messages.error(request, f'Error creating student: {e}')
        else:
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()
                    messages.success(request, f'User {user.username} created successfully!')
                    return redirect('custom_admin:admin_dashboard')
                except Exception as e:
                    logger.error(f"Error creating user: {e}")
                    messages.error(request, f'Error creating user: {e}')
        if not form.is_valid():
            logger.warning(f"Invalid form data: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        if role == 'Student':
            form = StudentRegistrationForm()
        else:
            form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'role': role
    }
    return render(request, 'student_marks/admin/create_user.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def django_admin_redirect(request):
    """Redirect superuser to Django admin interface"""
    return redirect('admin:index')

@login_required
@user_passes_test(is_admin)
def enter_marks(request):
    """View for entering marks by admin"""
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            subject_id = request.POST.get('subject')
            marks = request.POST.get('marks')
            exam_date_id = request.POST.get('exam_date')
            session_id = request.POST.get('session')

            student = get_object_or_404(Student, student_id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            exam_date = get_object_or_404(ExamDate, id=exam_date_id)
            session = get_object_or_404(Session, id=session_id)

            # Create or update marks
            Marks.objects.update_or_create(
                student=student,
                subject=subject,
                exam_date=exam_date,
                session=session,
                defaults={'score': marks}
            )

            messages.success(request, 'Marks entered successfully!')
        except Exception as e:
            logger.error(f"Error entering marks: {e}")
            messages.error(request, f'Error entering marks: {e}')

    # Get all required data for the form
    students = Student.objects.all()
    subjects = Subject.objects.all()
    exam_dates = ExamDate.objects.all()
    sessions = Session.objects.all()

    context = {
        'students': students,
        'subjects': subjects,
        'exam_dates': exam_dates,
        'sessions': sessions,
    }
    return render(request, 'student_marks/admin/enter_marks.html', context)

@login_required
@user_passes_test(is_teacher)
def student_marks(request, student_id):
    try:
        student = Student.objects.get(student_id=student_id)
        marks = Marks.objects.filter(student=student).order_by('-exam_date__date_of_exam')
        
        context = {
            'student': student,
            'marks': marks,
        }
        return render(request, 'student_marks/teacher/student_marks.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('teacher:dashboard')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('teacher:dashboard')

@login_required
@user_passes_test(is_student)
def student_marks_view(request):
    student = Student.objects.get(user=request.user)
    marks = Marks.objects.filter(student=student).order_by('exam_date', 'subject__name')
    
    # Get filter values
    session_filter = request.GET.get('session')
    exam_date_filter = request.GET.get('exam_date')
    
    # Apply filters
    if session_filter:
        marks = marks.filter(session__id=session_filter)
    if exam_date_filter:
        marks = marks.filter(exam_date__id=exam_date_filter)
    
    # Calculate statistics
    total_marks = marks.aggregate(total=models.Sum('score'))['total'] or 0
    avg_marks = marks.aggregate(avg=models.Avg('score'))['avg'] or 0
    max_marks = marks.aggregate(max=models.Max('score'))['max'] or 0
    min_marks = marks.aggregate(min=models.Min('score'))['min'] or 0
    
    context = {
        'marks': marks,
        'sessions': Session.objects.all(),
        'exam_dates': ExamDate.objects.all(),
        'total_marks': total_marks,
        'avg_marks': round(avg_marks, 2),
        'max_marks': max_marks,
        'min_marks': min_marks,
    }
    return render(request, 'student_marks/student/student_marks.html', context)

@login_required
@user_passes_test(is_student)
def student_visualize_data(request):
    student = Student.objects.get(user=request.user)
    marks = Marks.objects.filter(student=student)
    
    # Get filter values
    session_filter = request.GET.get('session')
    exam_date_filter = request.GET.get('exam_date')
    
    # Apply filters
    if session_filter:
        marks = marks.filter(session__id=session_filter)
    if exam_date_filter:
        marks = marks.filter(exam_date__id=exam_date_filter)
    
    # Generate visualizations
    subject_wise = subject_wise_analysis(marks)
    performance = student_performance_analysis(marks)
    report = generate_student_report(student.id)
    
    context = {
        'sessions': Session.objects.all(),
        'exam_dates': ExamDate.objects.all(),
        'subject_wise_chart': subject_wise,
        'performance_chart': performance,
        'student_report': report,
    }
    return render(request, 'student_marks/student/visualize_data.html', context)

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('custom_admin:admin_dashboard')
        elif hasattr(request.user, 'teacher'):
            return redirect('teacher:dashboard')
        elif hasattr(request.user, 'student'):
            return redirect('student:dashboard')
    return redirect('login')

@login_required
@user_passes_test(is_teacher)
def teacher_students(request):
    """View for teachers to see list of all students"""
    try:
        students = Student.objects.all().order_by('full_name')
        context = {
            'students': students,
        }
        return render(request, 'student_marks/teacher/students.html', context)
    except Exception as e:
        logger.error(f"Error in teacher_students view: {e}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('teacher:dashboard')

@login_required
@user_passes_test(is_admin)
def manage_students(request):
    students = Student.objects.all()
    return render(request, 'student_marks/admin/manage_students.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def manage_teachers(request):
    teachers = Teacher.objects.all()
    return render(request, 'student_marks/admin/manage_teachers.html', {'teachers': teachers})

@login_required
@user_passes_test(is_admin)
def manage_subjects(request):
    subjects = Subject.objects.all()
    return render(request, 'student_marks/admin/manage_subjects.html', {'subjects': subjects})

@login_required
@user_passes_test(is_admin)
def manage_classes(request):
    classes = StudentClass.objects.all()
    return render(request, 'student_marks/admin/manage_classes.html', {'classes': classes})

@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    courses = Course.objects.all()
    return render(request, 'student_marks/admin/manage_courses.html', {'courses': courses})

@login_required
@user_passes_test(is_admin)
def manage_sessions(request):
    sessions = Session.objects.all()
    return render(request, 'student_marks/admin/manage_sessions.html', {'sessions': sessions})

@login_required
@user_passes_test(is_admin)
def manage_exam_dates(request):
    exam_dates = ExamDate.objects.all()
    return render(request, 'student_marks/admin/manage_exam_dates.html', {'exam_dates': exam_dates})

@login_required
@user_passes_test(is_admin)
def manage_marks(request):
    marks = Marks.objects.all()
    return render(request, 'student_marks/admin/manage_marks.html', {'marks': marks})

@login_required
@user_passes_test(is_admin)
def view_marks(request):
    marks = Marks.objects.all().order_by('exam_date', 'student__full_name', 'subject__name')
    return render(request, 'student_marks/admin/view_marks.html', {'marks': marks})

@csrf_exempt
def power_bi_data(request):
    """API endpoint for Power BI dashboard"""
    try:
        # Get filter values from request
        session_id = request.GET.get('session')
        class_id = request.GET.get('class')
        course_id = request.GET.get('course')
        student_id = request.GET.get('student_id')
        exam_date_str = request.GET.get('exam_date')
        
        # Start with base queryset
        marks = Marks.objects.select_related(
            'student', 'subject', 'student__student_class', 'student__course', 'session', 'exam_date'
        )
        
        # Apply filters
        if session_id and session_id != 'None':
            marks = marks.filter(session_id=session_id)
            
        if class_id and class_id != 'None':
            marks = marks.filter(student__student_class_id=class_id)
            
        if course_id and course_id != 'None':
            marks = marks.filter(student__course_id=course_id)
            
        if student_id and student_id != 'None':
            marks = marks.filter(student__student_id=student_id)
            
        if exam_date_str:
            try:
                from datetime import datetime
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
                marks = marks.filter(exam_date__date_of_exam=exam_date)
            except ValueError:
                pass
        
        # Prepare data for Power BI
        data = []
        for mark in marks:
            data.append({
                'student_id': mark.student.student_id,
                'student_name': mark.student.full_name,
                'subject': mark.subject.name,
                'score': mark.score,
                'class': mark.student.student_class.name,
                'course': mark.student.course.name,
                'session': mark.session.session_name,
                'exam_date': mark.exam_date.date_of_exam.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'status': 'success',
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error in power_bi_data: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def detailed_student_analysis(request, student_id):
    """Detailed student performance analysis view"""
    try:
        student = get_object_or_404(Student, student_id=student_id)
        marks = Marks.objects.filter(student=student).select_related(
            'subject', 'exam_date'
        ).order_by('exam_date__date_of_exam')

        # 1. Time-based Analysis
        time_series_data = {}
        for mark in marks:
            date = mark.exam_date.date_of_exam
            if date not in time_series_data:
                time_series_data[date] = {
                    'total': 0,
                    'max_total': 0,
                    'count': 0,
                    'percentage': 0
                }
            time_series_data[date]['total'] += mark.score
            time_series_data[date]['max_total'] += max_marks.get(mark.subject.name, 100)
            time_series_data[date]['count'] += 1

        timeline_labels = [date.strftime('%Y-%m-%d') for date in sorted(time_series_data.keys())]
        timeline_total_marks = [time_series_data[date]['total'] for date in sorted(time_series_data.keys())]
        timeline_max_marks = [time_series_data[date]['max_total'] for date in sorted(time_series_data.keys())]
        timeline_percentages = [(time_series_data[date]['total'] / time_series_data[date]['max_total']) * 100 
                              for date in sorted(time_series_data.keys())]

        # 2. Subject-wise Progress
        subject_progress = {}
        for mark in marks:
            subject = mark.subject.name
            if subject not in subject_progress:
                subject_progress[subject] = []
            percentage = (mark.score / max_marks.get(subject, 100)) * 100
            subject_progress[subject].append({
                'date': mark.exam_date.date_of_exam.strftime('%Y-%m-%d'),
                'percentage': round(percentage, 2)
            })

        # 3. Class Comparison
        class_marks = Marks.objects.filter(
            student__student_class=student.student_class,
            exam_date__in=marks.values('exam_date')
        ).select_related('subject', 'exam_date')

        class_averages = {}
        for mark in class_marks:
            date = mark.exam_date.date_of_exam
            subject = mark.subject.name
            key = f"{date}_{subject}"
            if key not in class_averages:
                class_averages[key] = {'total': 0, 'count': 0}
            percentage = (mark.score / max_marks.get(subject, 100)) * 100
            class_averages[key]['total'] += percentage
            class_averages[key]['count'] += 1

        # Calculate student's percentile
        student_percentiles = {}
        for mark in marks:
            date = mark.exam_date.date_of_exam
            subject = mark.subject.name
            student_score = (mark.score / max_marks.get(subject, 100)) * 100
            
            all_scores = [
                (m.score / max_marks.get(m.subject.name, 100)) * 100
                for m in class_marks.filter(
                    exam_date__date_of_exam=date,
                    subject__name=subject
                )
            ]
            
            if all_scores:
                below_count = sum(1 for score in all_scores if score <= student_score)
                percentile = (below_count / len(all_scores)) * 100
                student_percentiles[f"{date}_{subject}"] = round(percentile, 2)

        # 4. Improvement Areas
        subject_averages = {}
        for subject, progress in subject_progress.items():
            if progress:
                avg = sum(item['percentage'] for item in progress) / len(progress)
                subject_averages[subject] = round(avg, 2)

        weak_subjects = [
            subject for subject, avg in subject_averages.items()
            if avg < 70  # Consider subjects with average below 70% as weak areas
        ]

        # 5. Recent Performance Trend
        recent_marks = marks.order_by('-exam_date__date_of_exam')[:5]
        recent_performance = []
        for mark in recent_marks:
            percentage = (mark.score / max_marks.get(mark.subject.name, 100)) * 100
            recent_performance.append({
                'date': mark.exam_date.date_of_exam.strftime('%Y-%m-%d'),
                'subject': mark.subject.name,
                'percentage': round(percentage, 2),
                'date_subject': f"{mark.exam_date.date_of_exam}_{mark.subject.name}"
            })

        context = {
            'student': student,
            'timeline_labels': timeline_labels,
            'timeline_total_marks': timeline_total_marks,
            'timeline_max_marks': timeline_max_marks,
            'timeline_percentages': timeline_percentages,
            'subject_progress': subject_progress,
            'class_averages': class_averages,
            'student_percentiles': student_percentiles,
            'subject_averages': subject_averages,
            'weak_subjects': weak_subjects,
            'recent_performance': recent_performance,
            'max_marks': max_marks
        }

        return render(request, 'student_marks/teacher/detailed_student_analysis.html', context)

    except Exception as e:
        logger.error(f"Error in detailed_student_analysis: {e}", exc_info=True)
        messages.error(request, "विस्तृत विश्लेषण में त्रुटि। कृपया फिर से कोशिश करें।")
        return redirect('teacher:dashboard')

@login_required
@user_passes_test(lambda u: is_teacher(u) or is_admin(u))
def exam_date_marks(request):
    """View to display all students' marks for a specific exam date"""
    try:
        # Get exam date from request
        exam_date_id = request.GET.get('exam_date')
        if not exam_date_id:
            messages.error(request, "कृपया परीक्षा तिथि चुनें")
            return redirect('teacher:visualize_data')
            
        exam_date = get_object_or_404(ExamDate, id=exam_date_id)
        
        # Get all marks for this exam date
        marks = Marks.objects.filter(exam_date=exam_date).select_related(
            'student', 'subject', 'student__student_class', 'student__course'
        ).order_by('student__full_name', 'subject__name')
        
        # Group marks by student
        student_marks = {}
        for mark in marks:
            student = mark.student
            if student not in student_marks:
                student_marks[student] = {
                    'student_id': student.student_id,
                    'full_name': student.full_name,
                    'class': student.student_class.name,
                    'course': student.course.name,
                    'subjects': {},
                    'total': 0,
                    'percentage': 0
                }
            
            subject_name = mark.subject.name
            max_mark = max_marks.get(subject_name, 100)
            percentage = (mark.score / max_mark) * 100
            
            student_marks[student]['subjects'][subject_name] = {
                'score': mark.score,
                'max_marks': max_mark,
                'percentage': round(percentage, 2)
            }
            
            student_marks[student]['total'] += mark.score
            student_marks[student]['percentage'] += percentage
        
        # Calculate average percentage for each student
        for student_data in student_marks.values():
            if student_data['subjects']:
                student_data['percentage'] = round(student_data['percentage'] / len(student_data['subjects']), 2)
        
        # Convert to list and sort by percentage in descending order
        sorted_marks = sorted(
            student_marks.values(),
            key=lambda x: x['percentage'],
            reverse=True
        )
        
        context = {
            'exam_date': exam_date,
            'student_marks': sorted_marks,
            'max_marks': max_marks
        }
        
        return render(request, 'student_marks/teacher/exam_date_marks.html', context)
        
    except Exception as e:
        logger.error(f"Error in exam_date_marks view: {e}", exc_info=True)
        messages.error(request, "एक त्रुटि उत्पन्न हुई। कृपया फिर से कोशिश करें।")
        return redirect('teacher:visualize_data')
