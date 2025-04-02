from django.db import models
from django.contrib.auth.models import User

class Session(models.Model):
    id = models.AutoField(primary_key=True)
    session_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.session_name

class StudentClass(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ExamDate(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_of_exam = models.DateField(unique=True)

    def __str__(self):
        return str(self.date_of_exam)


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('name', 'student_class', 'course')

    def __str__(self):
        return self.name

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name

class Marks(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    exam_date = models.ForeignKey(ExamDate, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        unique_together = ('session', 'exam_date', 'student_class', 'course', 'student', 'subject')

    def __str__(self):
        return f"{self.student.student_id} - {self.student.full_name} - {self.subject.name} ({self.score})"
