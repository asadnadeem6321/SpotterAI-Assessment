from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'tripplanner-api',
        'message': 'Django backend is running successfully.'
    })
