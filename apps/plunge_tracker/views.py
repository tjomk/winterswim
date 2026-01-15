from django.shortcuts import render

def plunge_list(request):
    return render(request, 'plunge_tracker/plunge_list.html', {})