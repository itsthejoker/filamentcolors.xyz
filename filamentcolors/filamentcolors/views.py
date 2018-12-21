from django.shortcuts import render


def homepage(request):
    html = 'home.html'

    return render(request, html)
