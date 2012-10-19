from django.shortcuts import render_to_response

def home(request):
    return render_to_response('base/index.html', {
        'read_only': getattr(request, 'read_only', False),
    })
