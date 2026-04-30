from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.users.urls')),
    path('courses/', include('apps.courses.urls')),
    path('quizzes/', include('apps.quizzes.urls')),
    path('assignments/', include('apps.assignments.urls')),
    path('practice/', include('apps.practice.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
