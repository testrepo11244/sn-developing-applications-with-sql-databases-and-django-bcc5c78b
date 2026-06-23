from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    """Course model representing an online course."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Lesson model belonging to a Course."""
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    """Question model for exam questions."""
    lesson = models.ForeignKey(Lesson, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"Q: {self.text[:50]}"


class Choice(models.Model):
    """Choice model for each possible answer."""
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


class Submission(models.Model):
    """Submission model storing a user's answers for a lesson exam."""
    user = models.ForeignKey(User, related_name='submissions', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='submissions', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.score})"


class Answer(models.Model):
    """Intermediate model linking a Submission to the selected Choices."""
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"{self.submission} - Q{self.question.id}"