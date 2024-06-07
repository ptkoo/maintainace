from django.urls import path
from . import views
from django.urls import include
from django.views.generic import RedirectView

urlpatterns = [
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('', RedirectView.as_view(url='index/', permanent=True)),
    # path('', RedirectView.as_view(url='index', permanent=True)),
    path('accounts/login/', views.handle_login, name = 'login'),
    path('',views.handle_login,name='login'),
    path('user', views.user, name = 'user'),
    path('chief', views.chief, name = 'chief'),
    path('officer', views.officer, name = 'officer'), 
    path('upload', views.upload_report, name='upload_report'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('update_report/<int:report_id>/', views.update_report, name='update_report'),
    path('solution/<int:report_id>/', views.solution, name = 'solution'),
    path('solutionForReport/<int:report_id>/', views.solutionForReport, name = 'solutionForReport'),
    path('upload_solution/<int:report_id>/', views.upload_solution, name='upload_solution'),
    path('reports/<str:operation_line>/', views.get_reports_by_status_and_profession, name='get_reports_by_operation_line'),
    path('dashboard', views.dashboard, name= 'dashboard'),
    path('error', views.error, name='error'),
    path('success', views.success, name='success'),

]
