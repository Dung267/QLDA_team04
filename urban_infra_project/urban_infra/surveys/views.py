from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Survey, SurveyResponse

@login_required
def survey_list(request):
    surveys = Survey.objects.filter(is_active=True)
    return render(request,'surveys/list.html',{'surveys':surveys,'page_title':'Khảo sát'})

@login_required
def survey_respond(request, pk):
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method=='POST':
        score = request.POST.get('satisfaction_score')
        comments = request.POST.get('comments','')
        SurveyResponse.objects.create(
            survey=survey, respondent=request.user,
            satisfaction_score=score, comments=comments
        )
        messages.success(request,'Cảm ơn bạn đã tham gia khảo sát!')
        return redirect('surveys:list')
    return render(request,'surveys/respond.html',{'survey':survey,'page_title':survey.title})
