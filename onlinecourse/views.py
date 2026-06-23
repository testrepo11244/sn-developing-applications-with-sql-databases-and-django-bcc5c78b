from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Course, Learner, Submission, Choice, Question

def submit(request, course_id):
    """
    Handles the submission of an exam for a given course.
    - Retrieves the Course and the authenticated Learner.
    - Creates a Submission instance.
    - Associates the selected Choice objects with the Submission.
    - Redirects to the result view.
    """
    course = get_object_or_404(Course, pk=course_id)

    # Assuming the user is authenticated and has a related Learner profile
    if not hasattr(request.user, "learner"):
        return HttpResponse("Learner profile not found.", status=400)
    learner = request.user.learner

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
                    # Skip malformed or non‑existent choice IDs
                    continue

        submission.save()
        # After saving, redirect to the result page
        return redirect("show_exam_result", submission_id=submission.id)

    # If GET request, render the exam page (template not required for grading)
    questions = course.question_set.all()
    return render(request, "exam.html", {"course": course, "questions": questions})


def show_exam_result(request, submission_id):
    """
    Displays the result of a submitted exam.
    - Calculates the total number of questions.
    - Determines how many questions were answered correctly.
    - Computes a percentage score.
    - Renders a result template with the calculated data.
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    course = submission.course
    total_questions = course.question_set.count()
    correct_answers = 0

    for question in course.question_set.all():
        # All choices the learner selected for this question
        selected_choices = submission.choices.filter(question=question)
        # All correct choices for this question
        correct_choices = question.choice_set.filter(is_correct=True)

        # A question is correct only if the selected set matches the correct set exactly
        if set(selected_choices) == set(correct_choices):
            correct_answers += 1

    score = int((correct_answers / total_questions) * 100) if total_questions else 0

    context = {
        "submission": submission,
        "course": course,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score,
    }
    return render(request, "exam_result.html", context)