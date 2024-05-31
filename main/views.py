from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Report, Profile, Image,Profession, OperationLine
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from .forms import ReportForm
import datetime
import os 
import mimetypes
from datetime import datetime as dateTime
# Create your views here.
def handle_login(request):
    if( request.method == 'POST'):
        form = AuthenticationForm(request, data= request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username= username, password= password)
            # print(user)
            if user is not None:
                login(request, user)  # Log the user in
                if user.groups.filter(name='User').exists():
                    redirect_url = '/main/user'
                elif user.groups.filter(name='Chief').exists():
                    redirect_url = '/main/chief'
                elif user.groups.filter(name='Officer').exists():
                    redirect_url = '/main/officer'
                elif user.groups.filter(name = "Repair").exists():
                    redirect_url = '/main/repair'
                else:
                    messages.error(request, "No group found for the user.")
                    return redirect('/main/accounts/login/')
                return redirect(redirect_url)
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('/main/accounts/login/')
        else:
            messages.error(request, "Form is not valid. Please check your username and password.")
            return redirect('/main/accounts/login/')
    
            
    return render(request, 'registration/login.html')


@login_required(login_url='/main/error')
def user(request):
    # Assuming reports_per_page is the number of reports you want to show per page
    reports_per_page = 1
    reports = Report.objects.filter(reporterName=request.user.username).order_by('-datetime')
    paginator = Paginator(reports, reports_per_page)

    # Get all the professions and operations Line number
    professions = Profession.objects.all()
    operation_lines = OperationLine.objects.all()

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'professions': professions,
        'operation_lines': operation_lines,
    }

    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        report = Report.objects.get(reportID = report_id)
        print(report)

        if request.POST.get('cancel') == 'Cancel':
            context = {
        'page_obj': page_obj,
        'professions': professions,
        'operation_lines': operation_lines,
        } 
        else: 
            context = {
            'page_obj': page_obj,
            'professions': professions,
            'operation_lines': operation_lines,
            'editReport' : report
        }


    return render(request, 'user.html', context)

@login_required(login_url='/main/error')
def chief(request):
    user = User.objects.get(username=request.user)
    profile = Profile.objects.get(user=user)
    operation_lines = profile.operation_line_no.all()
    operation_line_nos = [line.line_no for line in operation_lines]
    print("OperationLineNo", operation_line_nos)
    # reports = Report.objects.filter(status='0',operationLineNumber__in=operation_line_nos)  # Filter reports with status = '0'
    reports = Report.objects.filter(status='0', operationLineNumber__in= operation_line_nos)  # Filter reports with status = '0'

    # Pagination
    reports_per_page = 1
    paginator = Paginator(reports, reports_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # print("page_obj ",page_obj)
    
    # context = {
    #     'reports': reports,
    # }
    if request.method == 'POST':
        if 'confirm' in request.POST:
            report_id = request.POST.get('confirm')
            report = Report.objects.get(reportID = report_id)
            report.status = '1'
            report.confirmedBy = request.user.username
            report.save()
           
        elif 'cancel' in request.POST:
            report_id = request.POST.get('cancel')
            report = Report.objects.get(reportID = report_id)
            report.delete()
            print("Delete report")
        return redirect('/main/chief')
    
    context = {
        'page_obj': page_obj,
    }

    return render(request, 'chief.html', context)

@login_required(login_url='/main/error')
def officer(request):

    # for officer profession
    user = User.objects.get(username=request.user)
    profile = Profile.objects.get(user=user)
    professions = profile.profession.all()
    profession = [profession.profession_name for profession in professions]
    # print("Profession", profession)

    # For user group General and retriving their emails 
    general_group = Group.objects.get(name='General')
    users_in_general = User.objects.filter(groups=general_group)
    emails = [user.email for user in users_in_general if user.email]

    reports = Report.objects.filter(status ='1',problemCategory__in = profession )
    print(reports)
     # Pagination
    reports_per_page = 1
    paginator = Paginator(reports, reports_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'emails' : emails,
    }

    # For send email
    if request.method == 'POST':
        # print("After sending", request.POST)
        selected_email = request.POST.get('selected_email')
        report_ID = request.POST.get('report_id')
        report = Report.objects.get(reportID = report_ID)
        report.status = '2'
        report.sentBy = request.user.username
        report.sentTo = selected_email
        report.emailNotifyDate = datetime.datetime.now()
        report.dueDate = datetime.datetime.now() + datetime.timedelta(days=3)
        report.save()

        html_content = render_to_string('email.html', {'report': report})
        text_content = strip_tags(html_content)  # Plain text version for email clients that don't support HTML
        subject = "Report Details"
        # message = "Please find the report details below."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [selected_email,]

        # Create email
        email = EmailMultiAlternatives(subject, text_content, email_from, recipient_list)
        email.attach_alternative(html_content, "text/html")

        # Prepare attachments
        attachments = []
        for image in report.images.all():
            # Get the absolute file path for the image
            image_path = os.path.join(settings.MEDIA_ROOT, str(image.imageData))
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    file_content = f.read()
                    mime_type, _ = mimetypes.guess_type(image_path)
                    attachments.append((image.imageData.name, file_content, mime_type))
            else:
                print(f"Image file not found: {image_path}")

        # Attach files
        for filename, content, mimetype in attachments:
            email.attach(filename, content, mimetype)

        # Send email
        email.send()

    return render(request, 'officer.html', context)

def upload_report(request):
    if request.method == 'POST':
        reporter_name = request.POST.get('reporterName')
        description = request.POST.get('description')
        line_number = request.POST.get('lineNumber')
        problemCategory = request.POST.get('problemCategory')
        images = request.FILES.getlist('images')  # Use getlist to get multiple files

        dt_now = datetime.datetime.now()

        latest_report = Report.objects.order_by('-reportID').first()
        if latest_report:
            next_reportID = latest_report.reportID + 1
        else:
            next_reportID  = 1

        report = Report(
            reportID=next_reportID,
            reporterName=reporter_name,
            operationLineNumber=line_number,
            problemDescription=description,
            datetime=dt_now,
            problemCategory=problemCategory
        )
        report.save()

        for image in images:
            print(image)
            Image.objects.create(report=report, imageData=image)

        return redirect('/main/user')

    return render(request, 'registration/user.html')

def error(request):
    return render(request, 'registration/error.html')


def delete_report(request, report_id):
    if request.POST.get('action') == 'delete':
        report = get_object_or_404(Report, reportID=report_id)
        report.delete()
    return redirect('user')

def update_report(request, report_id):
    
    report = Report.objects.get(reportID = report_id)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        line_number = request.POST.get('lineNumber')
        problemCategory = request.POST.get('problemCategory')
        images = request.FILES.getlist('images')  # Use getlist to get multiple files
        dt_now = datetime.datetime.now()

        # Update existing report
        report.operationLineNumber = line_number
        report.problemDescription = description
        report.datetime = dt_now
        report.problemCategory = problemCategory
        report.save()
        # Clear existing images associated with the report
        report.images.all().delete()
        for image in images:
            print(image)
            Image.objects.create(report=report, imageData=image)

        return redirect('user')
    else:
        return redirect('error')

