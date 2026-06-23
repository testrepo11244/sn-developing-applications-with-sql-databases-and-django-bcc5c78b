from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Question, Choice, Submission, Answer


@login_required
def submit(request):
    """
    Handles POST submissions of exam answers.
    Expects 'question_id' and 'choice_id' in the POST data.
    """
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        choice_id = request.POST.get('choice_id')

        question = get_object_or_404(Question, pk=question_id)
        selected_choice = get_object_or_404(Choice, pk=choice_id, question=question)

        submission, created = Submission.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={'selected_choice': selected_choice}
        )
        if not created:
            submission.selected_choice = selected_choice
            submission.save()

        # Create or update the corresponding Answer record
        Answer.objects.update_or_create(
            submission=submission,
            defaults={'is_correct': selected_choice.is_correct}
        )

        return redirect('onlinecourse:show_exam_result')
    else:
        # If not POST, redirect to a generic exam page (implementation dependent)
        return redirect('onlinecourse:exam_page')


@login_required
def show_exam_result(request):
    """
    Calculates the user's exam score and renders the result page.
    """
    submissions = Submission.objects.filter(user=request.user).select_related(
        'question', 'selected_choice'
    )
    total_questions = submissions.count()
    correct_answers = submissions.filter(selected_choice__is_correct=True).count()
    score_percent = (correct_answers / total_questions * 100) if total_questions else 0

    context = {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'score_percent': round(score_percent, 2),
        'submissions': submissions,
    }
    return render(request, 'exam_result.html', context)