from django.contrib import admin
from .models import Session, ExamDate, StudentClass, Course, Student, Subject, Marks, Teacher

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_name',)
    search_fields = ('session_name',)
    list_filter = ('course',)

@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    list_display = ('session', 'date_of_exam')
    search_fields = ('session__session_name',)
    list_filter = ('session',)

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'session')
    search_fields = ('name', 'session__session_name')
    list_filter = ('session',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_class')
    search_fields = ('name', 'student_class__name')
    list_filter = ('student_class',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'student_class', 'course')
    search_fields = ('student_id', 'full_name', 'student_class__name', 'course__name')
    list_filter = ('student_class', 'course')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'course')
    search_fields = ('name', 'course__name')
    list_filter = ('course',)

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'score', 'exam_date')
    search_fields = ('student__student_id', 'student__full_name', 'subject__name')
    list_filter = ('subject', 'exam_date', 'student__student_class')

admin.site.register(Teacher)