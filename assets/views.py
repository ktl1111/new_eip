from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'selection_screen_assets.html', {
        'data': 'TEST data'
    })