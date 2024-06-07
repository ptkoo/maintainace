from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorator import group_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Report, Profile, Image,Profession, OperationLine, Solution, ImageSolution
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from .forms import ReportForm
import datetime
import os 
import mimetypes
from datetime import datetime as dateTime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
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

                next_param = request.GET.get('next')
                if next_param:
                    return redirect(next_param)
                elif user.groups.filter(name='User').exists():
                    redirect_url = '/main/user'
                elif user.groups.filter(name='Chief').exists():
                    redirect_url = '/main/chief'
                elif user.groups.filter(name='Officer').exists():
                    redirect_url = '/main/officer'
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
@group_required('User')
def user(request):
    # Assuming reports_per_page is the number of reports you want to show per page
    reports_per_page = 1
    reports = Report.objects.filter(reporterName=request.user.username).order_by('-datetime')
    # For filtering 
    status = request.GET.get('status')

    
    if status in ['0', '1', '2','3']:  # Assuming '0', '1', '2' are your status values
        reports = reports.filter(status=status)
        paginator = Paginator(reports, reports_per_page)
    else: 
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
        'status': status
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
        'status': status
        } 
        else: 
            context = {
            'page_obj': page_obj,
            'professions': professions,
            'operation_lines': operation_lines,
            'editReport' : report,
            'status': status
        }


    return render(request, 'user.html', context)

@login_required(login_url='/main/error')
@group_required('Chief')
def chief(request):
    user = User.objects.get(username=request.user)
    profile = Profile.objects.get(user=user)
    operation_lines = profile.operation_line_no.all()
    operation_line_nos = [line.line_no for line in operation_lines]
    print("OperationLineNo", operation_line_nos)
    # reports = Report.objects.filter(status='0',operationLineNumber__in=operation_line_nos)  # Filter reports with status = '0'
    reports = Report.objects.filter(status='0', operationLineNumber__in= operation_line_nos)  # Filter reports with status = '0'
   # Filter for status '0', '1', and '4' separately and combine the results
    reportHistorys = Report.objects.filter(status='0', operationLineNumber__in=operation_line_nos) | \
            Report.objects.filter(status='1', operationLineNumber__in=operation_line_nos) | \
            Report.objects.filter(status='4', operationLineNumber__in=operation_line_nos)
    # Pagination
    reports_per_page = 1
    paginator = Paginator(reports, reports_per_page)
    paginatorHistory = Paginator(reportHistorys, reports_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_obj_history = paginatorHistory.get_page(page_number)
   
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
            report.status = '4'
            report.save()
        return redirect('/main/chief')
    
    context = {
        'page_obj': page_obj,
        'page_obj_history': page_obj_history,
    }

    return render(request, 'chief.html', context)

@login_required(login_url='/main/error')
@group_required('Officer')
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

        # link = request.build_absolute_uri(reverse('login'))
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

@login_required(login_url='/main/error')
@group_required('User')
def upload_report(request):
    if request.method == 'POST':
        reporter_name = request.POST.get('reporterName')
        description = request.POST.get('description')
        line_number = request.POST.get('lineNumber')
        problemCategory = request.POST.get('problemCategory')
        machineNumber = request.POST.get('machineNumber')
        images = request.FILES.getlist('images')  # Use getlist to get multiple files

        dt_now = datetime.datetime.now().replace(second=0, microsecond=0)
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
            problemCategory=problemCategory,
            machineNumber=machineNumber,
        )
        report.save()

        for image in images:
            print(image)
            Image.objects.create(report=report, imageData=image)

        return redirect('/main/user')

    return render(request, 'registration/user.html')



@login_required(login_url='/main/error')
@group_required('User')
def delete_report(request, report_id):
    if request.POST.get('action') == 'delete':
        report = get_object_or_404(Report, reportID=report_id)
        report.delete()
    return redirect('user')

@login_required(login_url='/main/error')
@group_required('User')
def update_report(request, report_id):
    
    report = Report.objects.get(reportID = report_id)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        line_number = request.POST.get('lineNumber')
        problemCategory = request.POST.get('problemCategory')
        machineNumber = request.POST.get('machineNumber')
        images = request.FILES.getlist('images')  # Use getlist to get multiple files
        dt_now = datetime.datetime.now()

        # Update existing report
        report.operationLineNumber = line_number
        report.problemDescription = description
        report.datetime = dt_now
        report.problemCategory = problemCategory
        report.machineNumber = machineNumber
        report.save()
        # Clear existing images associated with the report
        # report.images.all().delete()
        for image in images:
            print(image)
            Image.objects.create(report=report, imageData=image)

        return redirect('user')
    else:
        return redirect('error')

# @login_required(login_url='/main/error')
# @group_required('General')
# After loggin in the user from "General group" can report their solution
def solution(request, report_id):
    report = Report.objects.get(reportID = report_id)
    return render(request, 'solution.html', {'report': report})

# This one is for view the solution for report by the user. 
def solutionForReport(request, report_id):
    report = Report.objects.get(reportID = report_id)
    solution = Solution.objects.get(report = report)
    return render(request, 'solutionForReport.html', {'report': report, 'solution': solution})

# @login_required(login_url='/main/error')
# @group_required('General')
def upload_solution(request, report_id):
    report = Report.objects.get(reportID = report_id)
    print("report ",report)
    if request.method == 'POST':
        solver_name = request.user.username
        soldescription = request.POST.get('soldescription')
        images = request.FILES.getlist('solimages')

        dt_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        latest_solution = Solution.objects.order_by('-solutionID').first()
        if latest_solution:
            next_solutionID = latest_solution.solutionID + 1
        else:
            next_solutionID  = 1

        solution = Solution(
            report=report,
            solutionID=next_solutionID, 
            solverName=solver_name,
            solutionState=solution_state,
            description=soldescription,
            datetime=dt_now,
        )
        solution.save()

        for image in images:
            ImageSolution.objects.create(solution=solution, imageData=image)

        # Updating Report Status 

        report.status = '3'
        report.solvedBy = solver_name

        report.save()

        return redirect('/main/success')

    return redirect('/main/error')


def dashboard(request):
    # Get all the professions and operations Line number
    professions = Profession.objects.all()
    return render( request, 'dashborad.html', {'professions': professions})

def get_reports_by_status_and_profession(request, operation_line):
    status = request.GET.get('status')
    profession = request.GET.get('profession')
    
    if operation_line == 'recent':
        reports = Report.objects.all().order_by('-datetime')[:10]  # Adjust the number of recent reports as needed
    else:
        reports = Report.objects.filter(operationLineNumber=operation_line)

    if status in ['0', '1', '2', '3', '4']:
        reports = reports.filter(status=status)

    if profession:
        reports = reports.filter(problemCategory=profession)

    report_list = list(reports.values('reportID', 'reporterName', 'operationLineNumber', 'problemCategory', 'problemDescription', 'status', 'datetime'))

    return JsonResponse(report_list, safe=False)


def error(request):
    return render(request, 'error.html')

def success(request):
    return render(request, 'success.html')