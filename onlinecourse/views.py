"""Views for handling exam submission and result display."""

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseBadRequest

from .models import Course, Submission, Choice, Question


@login_required
def submit(request, course_id):
    """
    Handles the POST request when a learner submits answers for a course exam.

    Steps:
    1. Retrieve the Course instance.
    2. Create a new Submission linked to the current user (learner) and the course.
    3. Iterate over posted choice IDs, fetch each Choice, and associate it with the Submission.
    4. Redirect the learner to the result page for the created submission.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed for exam submission.")

    course = get_object_or_404(Course, pk=course_id)
    learner = request.user

    # Create a new submission record
    submission = Submission.objects.create(course=course, learner=learner)

    # Expecting POST data in the form: choice_<question_id> = <choice_id>
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                choice_id = int(value)
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
            except (ValueError, Choice.DoesNotExist):
                # Skip invalid choice entries
                continue

    # After processing all choices, redirect to the result view
    return redirect(reverse("show_exam_result", args=[submission.id]))


@login_required
def show_exam_result(request, submission_id):
    """
    Displays the exam result for a given submission.

    The view calculates the total number of questions, the number of correctly answered
    questions, and the percentage score. It then renders a template showing the
    learner's performance along with a congratulatory message if the score is
    80% or higher.
    """
    submission = get_object_or_404(Submission, pk=submission_id, learner=request.user)
    course = submission.course

    # Gather all questions for the course
    questions = Question.objects.filter(lesson__course=course).distinct()
    total_questions = questions.count()

    # Determine how many questions were answered correctly
    correct_answers = 0
    for question in questions:
        # All choices selected by the learner for this question
        selected_choices = submission.choices.filter(question=question)

        # Correct choices for the question
        correct_choices = Choice.objects.filter(question=question, is_correct=True)

        # A question is correct only if the selected set matches the correct set exactly
        if set(selected_choices) == set(correct_choices):
            correct_answers += 1

    score_percentage = (correct_answers / total_questions * 100) if total_questions else 0

    context = {
        "course": course,
        "submission": submission,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": round(score_percentage, 2),
        "passed": score_percentage >= 80,
    }

    return render(request, "onlinecourse/exam_result.html", context)