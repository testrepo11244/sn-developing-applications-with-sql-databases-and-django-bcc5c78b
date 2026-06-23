from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Submission, Choice, Question


@login_required
def submit(request, course_id):
    """
    Handles the exam submission for a given course.
    - Retrieves the course and the logged‑in learner.
    - Creates a Submission instance.
    - Associates the selected Choice objects with the submission.
    - Redirects to the result view after processing.
    """
    course = get_object_or_404(Course, pk=course_id)
    learner = request.user

    if request.method == "POST":
        # Create a new submission record
        submission = Submission.objects.create(course=course, learner=learner)

        # Expected POST data: choice_<question_id> = <choice_id>
        for key, value in request.POST.items():
            if key.startswith("choice_"):
                try:
                    choice_id = int(value)
                    choice = Choice.objects.get(pk=choice_id)
                    submission.choices.add(choice)
                except (ValueError, Choice.DoesNotExist):
                    # Ignore malformed or missing choice IDs
                    continue

        # After storing the choices, show the exam result
        return redirect("show_exam_result", submission_id=submission.id)

    # If GET request, render the exam page with all questions
    questions = Question.objects.filter(course=course).prefetch_related("choice_set")
    return render(
        request,
        "exam.html",
        {"course": course, "questions": questions},
    )


def show_exam_result(request, submission_id):
    """
    Displays the result of a completed exam.
    - Calculates the total number of questions.
    - Determines how many were answered correctly.
    - Computes a percentage score.
    - Renders the result template with the calculated data.
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    course = submission.course

    total_questions = course.question_set.count()
    correct_answers = 0

    for question in course.question_set.all():
        selected_choices = submission.choices.filter(question=question)
        # Assume Question model provides an `is_correct` helper
        if question.is_correct(selected_choices):
            correct_answers += 1

    score = int((correct_answers / total_questions) * 100) if total_questions else 0

    context = {
        "submission": submission,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score,
    }
    return render(request, "exam_result.html", context)