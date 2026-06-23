from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Course, Lesson, Question, Choice, Submission, Learner


@login_required
@transaction.atomic
def submit(request, course_id):
    """
    Handles the exam submission for a given course.
    Expects POST data where each key is ``question_<id>`` and the value is the selected
    ``Choice`` primary key.
    """
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)

    if request.method == 'POST':
        total_questions = 0
        correct_answers = 0

        for lesson in course.lessons.all():
            for question in lesson.questions.all():
                total_questions += 1
                selected_choice_id = request.POST.get(f'question_{question.id}')
                if selected_choice_id:
                    selected_choice = Choice.objects.filter(pk=selected_choice_id,
                                                            question=question).first()
                    if selected_choice and selected_choice.is_correct:
                        correct_answers += 1

        score = (correct_answers / total_questions) * 100 if total_questions else 0

        # Record the submission (associate with the first lesson for simplicity)
        submission = Submission.objects.create(
            learner=learner,
            lesson=course.lessons.first(),
            score=score
        )
        request.session['submission_id'] = submission.id
        return redirect('onlinecourse:show_exam_result', course_id=course.id)

    # GET request – render the exam page
    return render(request, 'exam.html', {'course': course})


@login_required
def show_exam_result(request, course_id):
    """
    Displays the result of the most recent exam submission for the logged‑in learner.
    """
    submission_id = request.session.get('submission_id')
    submission = get_object_or_404(Submission, pk=submission_id,
                                   learner__user=request.user)

    context = {
        'course': get_object_or_404(Course, pk=course_id),
        'submission': submission,
        'message': 'Congratulations! You have completed the exam.'
    }
    return render(request, 'exam_result.html', context)