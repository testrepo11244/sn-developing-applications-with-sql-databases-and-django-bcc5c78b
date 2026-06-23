from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from .models import Course, Submission, Choice

def submit(request, course_id):
    """
    Handles the submission of an exam for a given course.
    Expects POST data where each selected choice is sent with a key
    formatted as ``choice_<question_id>`` and the value being the
    primary key of the chosen ``Choice`` instance.
    """
    if request.method != "POST":
        # If the request is not POST, simply render the exam page.
        course = get_object_or_404(Course, pk=course_id)
        return render(request, "exam.html", {"course": course})

    # Retrieve the course and the learner (authenticated user)
    course = get_object_or_404(Course, pk=course_id)
    learner = request.user

    # Create a new Submission instance
    submission = Submission.objects.create(course=course, learner=learner)

    # Attach the selected choices to the submission
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                choice = Choice.objects.get(pk=int(value))
                submission.choices.add(choice)
            except (ValueError, Choice.DoesNotExist):
                # Skip malformed or non‑existent choice IDs
                continue

    submission.save()
    # Redirect to the result view after successful submission
    return redirect("show_exam_result", submission_id=submission.id)


def show_exam_result(request, submission_id):
    """
    Displays the result of a previously submitted exam.
    Calculates the total number of questions, the number of
    correctly answered questions, and the percentage score.
    """
    submission = get_object_or_404(Submission, pk=submission_id)

    # Total number of questions in the course (across all lessons)
    total_questions = (
        submission.course.lesson_set.aggregate(total=Count("question"))
        .get("total") or 0
    )

    # Count correctly selected choices (assuming each question has a single correct choice)
    correct_answers = sum(1 for choice in submission.choices.all() if choice.is_correct)

    score = int((correct_answers / total_questions) * 100) if total_questions else 0

    context = {
        "submission": submission,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score,
    }
    return render(request, "exam_result.html", context)