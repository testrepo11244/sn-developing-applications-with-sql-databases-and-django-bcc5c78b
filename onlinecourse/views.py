from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Learner, Submission, Choice, Question


@login_required
def submit(request, course_id):
    """
    Handles the submission of an exam for a given course.
    Creates a Submission instance, links the selected Choice objects,
    and redirects to the result view.
    """
    # Retrieve the course; 404 if not found
    course = get_object_or_404(Course, pk=course_id)

    # Assume the logged‑in user is a Learner; create if necessary
    learner, _ = Learner.objects.get_or_create(user=request.user)

    # Create a new Submission record
    submission = Submission.objects.create(
        learner=learner,
        course=course,
    )

    # Expected POST data format:
    #   choice_<question_id> = <choice_id>
    # Iterate over all questions in the course and attach the selected choices
    for question in course.question_set.all():
        choice_key = f"choice_{question.id}"
        choice_id = request.POST.get(choice_key)
        if choice_id:
            try:
                choice = Choice.objects.get(pk=int(choice_id), question=question)
                submission.choices.add(choice)
            except Choice.DoesNotExist:
                # Ignore invalid choice IDs – they will not affect scoring
                continue

    # After processing, redirect to the result page
    return redirect('show_exam_result', submission_id=submission.id)


@login_required
def show_exam_result(request, submission_id):
    """
    Displays the result of a completed exam.
    Calculates the total score based on the learner's selected choices.
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    course = submission.course
    learner = submission.learner

    total_score = 0
    max_score = 0
    question_results = []

    for question in course.question_set.all():
        max_score += question.grade
        selected_choices = submission.choices.filter(question=question)
        is_correct = all(
            choice.is_correct for choice in selected_choices
        ) and selected_choices.count() == question.choice_set.filter(is_correct=True).count()
        if is_correct:
            total_score += question.grade

        question_results.append({
            'question': question,
            'selected_choices': selected_choices,
            'is_correct': is_correct,
        })

    context = {
        'course': course,
        'learner': learner,
        'submission': submission,
        'total_score': total_score,
        'max_score': max_score,
        'question_results': question_results,
    }

    return render(request, 'onlinecourse/exam_result.html', context)