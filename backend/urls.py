"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def home_view(request):
    return HttpResponse(
        """
        <!doctype html>
        <html lang=\"en\">
          <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
            <title>Trip Planner</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 2rem; line-height: 1.6; }
              code { background: #f5f5f5; padding: 0.2rem 0.4rem; }
            </style>
          </head>
          <body>
            <h1>Trip Planner API</h1>
            <p>The backend is running.</p>
            <p>Open the React app at <a href=\"http://127.0.0.1:5173\">http://127.0.0.1:5173</a>.</p>
            <p>Health check: <code>/api/health/</code></p>
            <p>Trip planning API: <code>/api/trip-plan/</code></p>
          </body>
        </html>
        """,
        content_type='text/html',
    )


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('tripplanner.urls')),
]
