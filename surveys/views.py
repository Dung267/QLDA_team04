from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Survey, SurveyResponse


def survey_list(request):
    surveys = Survey.objects.filter(is_active=True)
    return render(request, 'surveys/list.html', {'surveys': surveys, 'page_title': 'Khảo sát'})


def survey_detail(request, pk):
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == 'POST':
        answers = {}
        for q in survey.questions.all():
            answers[str(q.pk)] = request.POST.get(f'q_{q.pk}', '')
        SurveyResponse.objects.create(
            survey=survey,
            respondent=request.user if request.user.is_authenticated else None,
            answers=answers,
            overall_rating=request.POST.get('overall_rating'),
        )
        messages.success(request, 'Cảm ơn bạn đã tham gia khảo sát!')
        return redirect('surveys:list')
    return render(request, 'surveys/detail.html', {'survey': survey, 'page_title': survey.title})


@login_required
def survey_results(request, pk):
    from django.db.models import Avg, Count
    survey = get_object_or_404(Survey, pk=pk)
    responses = survey.responses.all()
    stats = {
        'total_responses': responses.count(),
        'avg_rating': responses.aggregate(avg=Avg('overall_rating'))['avg'],
    }
    return render(request, 'surveys/results.html', {'survey': survey, 'stats': stats, 'page_title': f'Kết quả - {survey.title}'})
