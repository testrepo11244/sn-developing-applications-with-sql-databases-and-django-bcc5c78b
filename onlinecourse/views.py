from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Question, Choice, Submission, Answer, Learner


@login_required
def submit(request, course_id):
    """
    Handles the POST request when a learner submits answers for a course exam.
    Creates a ``Submission`` instance, records each selected ``Choice`` as an
    ``Answer`` and redirects to the result page.
    """
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if request.method == "POST":
        # Create a new submission record
        submission = Submission.objects.create(learner=learner, course=course)

        # Iterate over posted choices; expected format: question_<id>=<choice_id>
        for key, value in request.POST.items():
            if key.startswith("question_"):
                try:
                    choice_id = int(value)
                    choice = Choice.objects.get(pk=choice_id)
                    Answer.objects.create(submission=submission, choice=choice)
                except (ValueError, Choice.DoesNotExist):
                    continue  # ignore malformed data

        # After storing answers, calculate total score
        submission.calculate_score()

        # Redirect to result view
        return redirect(
            reverse(
                "show_exam_result",
                kwargs={"submission_id": submission.id},
            )
        )
    else:
        # Render exam page with questions and choices
        lessons = Lesson.objects.filter(course=course).prefetch_related(
            "questions__choices"
        )
        return render(
            request,
            "exam.html",
            {"course": course, "lessons": lessons},
        )


@login_required
def show_exam_result(request, submission_id):
    """
    Displays the result of a learner's exam attempt.
    Shows a congratulatory message, the total score and a breakdown of each
    question with the selected answer.
    """
    submission = get_object_or_404(Submission, pk=submission_id, learner__user=request.user)
    # Ensure score is up‑to‑date (in case it was not calculated earlier)
    submission.calculate_score()

    # Gather detailed answer info
    answers = submission.answers.select_related("choice__question").all()
    context = {
        "submission": submission,
        "answers": answers,
    }
    return render(request, "exam_result.html", context)