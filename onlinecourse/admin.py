from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Question,
    Choice,
    Submission,
    Answer,
    User,  # Assuming a custom user model is defined in the same app for import convenience
)

# Inline for Choice objects within a Question
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ('text', 'is_correct')
    readonly_fields = ()

# Inline for Question objects within a Lesson
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text',)
    inlines = [ChoiceInline]

# Admin for Question to manage its choices directly
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'lesson')
    search_fields = ('text',)
    list_filter = ('lesson__course',)
    inlines = [ChoiceInline]

# Admin for Lesson to manage its questions (and choices) directly
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title', 'course__title')
    list_filter = ('course',)
    inlines = [QuestionInline]

# Register models with the admin site
admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
admin.site.register(Answer)