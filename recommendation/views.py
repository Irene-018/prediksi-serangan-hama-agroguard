from django.shortcuts import render

def recommendation_page(request):
    return render(request, 'recommendation/recommendation.html')
