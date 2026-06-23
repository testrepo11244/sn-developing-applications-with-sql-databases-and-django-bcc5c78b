from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='instructor_profile'
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Instructor: {self.user.get_full_name() or self.user.username}"


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(
        Instructor, related_name='courses', blank=True
    )

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons'
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='questions'
    )
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"Question {self.id} for {self.lesson.title}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='choices'
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice for Q{self.question.id}: {self.text}"


class Submission(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submissions'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='submissions'
    )
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.CASCADE, related_name='+'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} for Q{self.question.id}"


class Answer(models.Model):
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name='answer'
    )
    is_correct = models.BooleanField()

    def __str__(self):
        return f"Answer for {self.submission}"