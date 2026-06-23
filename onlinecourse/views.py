from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Lesson, Question, Choice, Submission, Answer
from decimal import Decimal


@login_required
def submit(request, lesson_id):
    """
    Handles POST submission of an exam for a given lesson.
    Expects POST data in the form:
        choice_<question_id> = <choice_id>
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    if request.method != "POST":
        return HttpResponseForbidden("Only POST requests are allowed.")

    # Create a new Submission instance
    submission = Submission.objects.create(user=request.user, lesson=lesson)

    total_questions = lesson.questions.count()
    correct_answers = 0

    for question in lesson.questions.all():
        choice_key = f"choice_{question.id}"
        selected_choice_id = request.POST.get(choice_key)

        if not selected_choice_id:
            # No answer provided for this question; skip scoring
            continue

        selected_choice = get_object_or_404(Choice, pk=selected_choice_id, question=question)

        # Record the answer
        Answer.objects.create(
            submission=submission,
            question=question,
            selected_choice=selected_choice
        )

        if selected_choice.is_correct:
            correct_answers += 1

    # Calculate score as a percentage
    if total_questions:
        score = (Decimal(correct_answers) / Decimal(total_questions)) * 100
        submission.score = round(score, 2)
    else:
        submission.score = 0

    submission.save()

    return redirect(reverse('show_exam_result', args=[submission.id]))


@login_required
def show_exam_result(request, submission_id):
    """
    Displays the result of a specific exam submission.
    Shows a congratulatory message if the score is >= 70%.
    """
    submission = get_object_or_404(Submission, pk=submission_id, user=request.user)

    context = {
        "submission": submission,
        "passed": submission.score >= 70 if submission.score is not None else False,
    }
    return render(request, "exam_result.html", context)