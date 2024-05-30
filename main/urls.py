from django.urls import path
from . import views
from django.urls import include
from django.views.generic import RedirectView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='accounts/login/', permanent=True)),
    path('accounts/login', views.handle_login, name = 'login'),
    path('user', views.user, name = 'user'),
    path('chief', views.chief, name = 'chief'),
    path('officer', views.officer, name = 'officer'), 
    path('repair', views.repair, name = 'repair'),
    path('upload', views.upload_report, name='upload_report'),
    path('error', views.error, name='error'),
    path('sendMail', views.sendMail, name = 'sendMail')
]
