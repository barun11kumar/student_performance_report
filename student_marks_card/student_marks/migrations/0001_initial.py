# Generated by Django 5.1.7 on 2025-03-26 05:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Session",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("session_name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.session",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StudentClass",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.session",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("student_id", models.CharField(max_length=20, unique=True)),
                ("full_name", models.CharField(max_length=100)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.course",
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.session",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "student_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.studentclass",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExamDate",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("date_of_exam", models.DateField(unique=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.course",
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.session",
                    ),
                ),
                (
                    "student_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.studentclass",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="course",
            name="student_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="student_marks.studentclass",
            ),
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.course",
                    ),
                ),
                (
                    "student_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.studentclass",
                    ),
                ),
            ],
            options={
                "unique_together": {("name", "student_class", "course")},
            },
        ),
        migrations.CreateModel(
            name="Teacher",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=100)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Marks",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.IntegerField()),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.course",
                    ),
                ),
                (
                    "exam_date",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.examdate",
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.session",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.student",
                    ),
                ),
                (
                    "student_class",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.studentclass",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="student_marks.subject",
                    ),
                ),
            ],
            options={
                "unique_together": {
                    (
                        "session",
                        "exam_date",
                        "student_class",
                        "course",
                        "student",
                        "subject",
                    )
                },
            },
        ),
    ]
