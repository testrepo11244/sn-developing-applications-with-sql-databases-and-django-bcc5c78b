from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Submission,
    Learner,
    Instructor,
)


class ChoiceInline(admin.TabularInline):
    """Inline editing of Choices within a Question."""
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    """Inline editing of Questions within a Lesson."""
    model = Question
    extra = 1
    inlines = [ChoiceInline]  # Nest ChoiceInline inside QuestionInline (requires django-nested-admin or custom handling)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "lesson", "grade")
    list_filter = ("lesson",)
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin view for Lesson with inline Questions."""
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title",)
    inlines = [QuestionInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("learner", "course", "score", "submitted_at")
    list_filter = ("course", "learner")
    readonly_fields = ("score", "submitted_at")


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("user",)