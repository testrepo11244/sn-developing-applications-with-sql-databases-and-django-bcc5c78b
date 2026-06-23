from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Course, Submission, Choice, Question


@login_required
def submit(request, course_id):
    """
    Handles the POST request from the exam page.
    Creates a Submission instance for the logged‑in learner,
    attaches the selected Choice objects, and redirects to the
    result view.
    """
    course = get_object_or_404(Course, pk=course_id)
    learner = request.user

    if request.method != "POST":
        # In a real app this would render the exam template.
        return render(request, "exam.html", {"course": course})

    # Create a new submission record
    submission = Submission.objects.create(course=course, learner=learner)

    # Expected POST data: question_<question_id> = <choice_id>
    for key, value in request.POST.items():
        if not key.startswith("question_"):
            continue
        try:
            choice_id = int(value)
            choice = Choice.objects.get(pk=choice_id)
            submission.choices.add(choice)
        except (ValueError, Choice.DoesNotExist):
            # Skip malformed or missing choices
            continue

    submission.save()
    return redirect(
        "show_exam_result", submission_id=submission.id
    )


@login_required
def show_exam_result(request, submission_id):
    """
    Displays the result of a completed exam.
    Calculates the total number of questions, the number of
    correctly answered questions, and the percentage score.
    """
    submission = get_object_or_404(
        Submission, pk=submission_id, learner=request.user
    )
    questions = (
        Question.objects.filter(course=submission.course)
        .prefetch_related("choice_set")
        .all()
    )
    total_questions = questions.count()
    correct_answers = 0

    for question in questions:
        # IDs of the correct choices for this question
        correct_set = set(
            question.choice_set.filter(is_correct=True).values_list("id", flat=True)
        )
        # IDs of the learner's selected choices for this question
        selected_set = set(
            submission.choices.filter(question=question).values_list("id", flat=True)
        )
        if correct_set == selected_set:
            correct_answers += 1

    score = int((correct_answers / total_questions) * 100) if total_questions else 0

    context = {
        "submission": submission,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score,
    }
    return render(request, "exam_result.html", context)