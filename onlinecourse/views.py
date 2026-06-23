from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Learner, Submission, Choice, Question


@login_required
def submit(request, course_id):
    """
    Handles the POST request from the exam page.
    Creates a Submission instance for the logged‑in learner,
    attaches the selected Choice objects and redirects to the
    result view.
    """
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if request.method != "POST":
        # In a real app this would render the exam template.
        return render(request, "exam.html", {"course": course})

    # Create a new submission record
    submission = Submission.objects.create(course=course, learner=learner)

    # Expected POST keys: choice_<question_id> = <choice_id>
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                choice_id = int(value)
                choice = Choice.objects.get(pk=choice_id)
                submission.choices.add(choice)
            except (ValueError, Choice.DoesNotExist):
                # Ignore malformed data – continue processing other choices
                continue

    submission.save()
    return redirect("onlinecourse:show_exam_result", submission_id=submission.id)


@login_required
def show_exam_result(request, submission_id):
    """
    Calculates the exam score for a given submission and renders
    the result template.
    """
    submission = get_object_or_404(Submission, pk=submission_id)

    # All questions belonging to the course of this submission
    questions = Question.objects.filter(lesson__course=submission.course)
    total_questions = questions.count()
    correct_answers = 0

    for question in questions:
        # Choices the learner selected for this question
        selected = submission.choices.filter(question=question)

        # All correct choices for this question
        correct = Choice.objects.filter(question=question, is_correct=True)

        if set(selected) == set(correct):
            correct_answers += 1

    score = int((correct_answers / total_questions) * 100) if total_questions else 0

    context = {
        "submission": submission,
        "score": score,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
    }
    return render(request, "exam_result.html", context)