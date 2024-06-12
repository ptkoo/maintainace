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
from datetime import timedelta,  date
from datetime import datetime as dateTime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.db.models import Count
from django.utils import timezone
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
    reports = Report.objects.filter(status='0', operationLineNumber__in= operation_line_nos).order_by('-datetime')  # Filter reports with status = '0'
    # Filter for status '0', '1', and '4' separately and combine the results
    reportHistorys = Report.objects.filter(status='0', operationLineNumber__in=operation_line_nos) | \
            Report.objects.filter(status='1', operationLineNumber__in=operation_line_nos) | \
            Report.objects.filter(status='4', operationLineNumber__in=operation_line_nos).order_by('-datetime')
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

    reports = Report.objects.filter(status ='1',problemCategory__in = profession ).order_by('-datetime')
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
        
        # Send SSE update to notify chief about new report
        send_sse_update_to_chief()

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
            # solutionState=solution_state,
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
    return render( request, 'dashboard.html', {'professions': professions})

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


# For analysis dashboard

# This is for line and bar chart
def reports_daily(request, year, month):
    # Fetch all reports and convert the datetime string to a datetime object
    reports = Report.objects.all()
    report_list = []
    
    for report in reports:
        try:
            report_datetime = datetime.datetime.strptime(report.datetime, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue  # Skip if datetime format is incorrect
            
        report_list.append({
            'report': report,
            'datetime': report_datetime,
        })
    
    # Sort the reports by the datetime object in descending order
    sorted_reports = sorted(report_list, key=lambda x: x['datetime'], reverse=True)
    
    # Filter reports based on the chosen year and month, default to current month and year if not specified
    if year and month:
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            year = date.today().year
            month = date.today().month
    else:
        year = date.today().year
        month = date.today().month

    reports_for_month = [item for item in sorted_reports if item['datetime'].year == year and item['datetime'].month == month]
    
    # Group and count reports by day
    data = {}
    for item in reports_for_month:
        day = item['datetime'].date()
        if day not in data:
            data[day] = 0
        data[day] += 1
    
    sorted_data = sorted(data.items())
    sorted_data = [{'day': str(day), 'count': count} for day, count in sorted_data]
    
    return JsonResponse(sorted_data, safe=False)


# This is for line and bar chart
def reports_monthly(request, year=None):
    # Fetch all reports and convert the datetime string to a datetime object
    reports = Report.objects.all()
    report_list = []
    
    for report in reports:
        try:
            report_datetime = datetime.datetime.strptime(report.datetime, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue  # Skip if datetime format is incorrect
            
        report_list.append({
            'report': report,
            'datetime': report_datetime,
        })
    
    # Sort the reports by the datetime object in descending order
    sorted_reports = sorted(report_list, key=lambda x: x['datetime'], reverse=True)
    
    # Filter reports for the chosen year or default to current year
    if year:
        try:
            year = int(year)
        except ValueError:
            year = date.today().year
    else:
        year = date.today().year
        
    reports_for_year = [item for item in sorted_reports if item['datetime'].year == year]
    
    # Group and count reports by month
    data = {}
    for item in reports_for_year:
        month = (item['datetime'].year, item['datetime'].month)
        if month not in data:
            data[month] = 0
        data[month] += 1
    
    sorted_data = sorted(data.items())
    sorted_data = [{'month': f'{year}-{month:02}', 'count': count} for (year, month), count in sorted_data]
    
    return JsonResponse(sorted_data, safe=False)


# def reports_today(request):
#     # Get current date
#     current_date = date.today()
    
#     # Fetch all reports (assuming datetime is a char field)
#     reports = Report.objects.all()
    
#     # Filter reports for the current day
#     reports_today = [report for report in reports if report.datetime.startswith(str(current_date))]
    
#     # Group and count reports by problem category
#     categories_data = {}
#     for report in reports_today:
#         if report.problemCategory in categories_data:
#             categories_data[report.problemCategory] += 1
#         else:
#             categories_data[report.problemCategory] = 1
    
#     # Convert categories_data into the format required by Chart.js
#     categories_labels = list(categories_data.keys())
#     categories_counts = list(categories_data.values())
    
#     # Group and count reports by status
#     statuses_data = {}
#     for report in reports_today:
#         if report.status in statuses_data:
#             statuses_data[report.status] += 1
#         else:
#             statuses_data[report.status] = 1
    
#     # Convert statuses_data into the format required by Chart.js
#     statuses_labels = list(statuses_data.keys())
#     statuses_counts = list(statuses_data.values())
    
#     data = {
#         'categories_labels': categories_labels,
#         'categories_counts': categories_counts,
#         'statuses_labels': statuses_labels,
#         'statuses_counts': statuses_counts,
#     }
    
#     return JsonResponse(data)

# def reports_currentMonth(request):
#     today = date.today()
#     first_day_of_month = today.replace(day=1)
#     last_day_of_month = today.replace(day=1, month=today.month % 12 + 1) - datetime.timedelta(days= 1)
    
#     # Fetch all reports (assuming datetime is a char field)
#     reports = Report.objects.all()
    
#     # Fetch reports for the current month
#     reports_currentMonth = Report.objects.filter(
#         datetime__gte=first_day_of_month,
#         datetime__lte=last_day_of_month
#     )
    
#     # Group and count reports by problem category
#     categories_data = {}
#     for report in reports_currentMonth:
#         if report.problemCategory in categories_data:
#             categories_data[report.problemCategory] += 1
#         else:
#             categories_data[report.problemCategory] = 1
    
#     # Convert categories_data into the format required by Chart.js
#     categories_labels = list(categories_data.keys())
#     categories_counts = list(categories_data.values())
    
#     # Group and count reports by status
#     statuses_data = {}
#     for report in reports_currentMonth:
#         if report.status in statuses_data:
#             statuses_data[report.status] += 1
#         else:
#             statuses_data[report.status] = 1
    
#     # Convert statuses_data into the format required by Chart.js
#     statuses_labels = list(statuses_data.keys())
#     statuses_counts = list(statuses_data.values())
    
#     data = {
#         'categories_labels': categories_labels,
#         'categories_counts': categories_counts,
#         'statuses_labels': statuses_labels,
#         'statuses_counts': statuses_counts,
#     }
    
#     return JsonResponse(data)


def reports_currentMonth(request, year, month):
    # Get current date
    current_date = date.today()
    
    # Fetch all reports (assuming datetime is a char field)
    reports = Report.objects.all()
    
    # Determine the target year and month based on input parameters
    if year and month:
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return JsonResponse({'error': 'Invalid year or month format'}, status=400)
    elif year:
        try:
            year = int(year)
            month = 1  # Default to January if only year is specified
        except ValueError:
            return JsonResponse({'error': 'Invalid year format'}, status=400)
    else:
        year = current_date.year
        month = current_date.month
    # Filter reports for the specified month and year
    reports_filtered = [
        report for report in reports
        if report.datetime.startswith(f"{year}-{month:02}")
    ]
    
    # Group and count reports by problem category
    categories_data = {}
    for report in reports_filtered:
        if report.problemCategory in categories_data:
            categories_data[report.problemCategory] += 1
        else:
            categories_data[report.problemCategory] = 1
    
    # Convert categories_data into the format required by Chart.js
    categories_labels = list(categories_data.keys())
    categories_counts = list(categories_data.values())
    
    # Group and count reports by status
    statuses_data = {}
    for report in reports_filtered:
        if report.status in statuses_data:
            statuses_data[report.status] += 1
        else:
            statuses_data[report.status] = 1
    
    # Convert statuses_data into the format required by Chart.js
    statuses_labels = list(statuses_data.keys())
    statuses_counts = list(statuses_data.values())
    
    data = {
        'categories_labels': categories_labels,
        'categories_counts': categories_counts,
        'statuses_labels': statuses_labels,
        'statuses_counts': statuses_counts,
    }
    
    return JsonResponse(data)


def reports_today(request, year=None, month=None, day=None):
    # Get current date
    current_date = date.today()
    
    # Fetch all reports (assuming datetime is a char field)
    reports = Report.objects.all()

    # Determine the target date based on input parameters
    if year and month and day:
        try:
            target_date = datetime.datetime.strptime(f'{year}-{month}-{day}', '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid year, month, or day format'}, status=400)
    elif year and month:
        try:
            target_date = datetime.datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid year or month format'}, status=400)
    else:
        target_date = current_date

    # Filter reports for the target date
    reports_filtered = [report for report in reports if report.datetime.startswith(str(target_date))]

    # Group and count reports by problem category
    categories_data = {}
    for report in reports_filtered:
        if report.problemCategory in categories_data:
            categories_data[report.problemCategory] += 1
        else:
            categories_data[report.problemCategory] = 1
    
    # Convert categories_data into the format required by Chart.js
    categories_labels = list(categories_data.keys())
    categories_counts = list(categories_data.values())
    
    # Group and count reports by status
    statuses_data = {}
    for report in reports_filtered:
        if report.status in statuses_data:
            statuses_data[report.status] += 1
        else:
            statuses_data[report.status] = 1
    
    # Convert statuses_data into the format required by Chart.js
    statuses_labels = list(statuses_data.keys())
    statuses_counts = list(statuses_data.values())
    
    data = {
        'categories_labels': categories_labels,
        'categories_counts': categories_counts,
        'statuses_labels': statuses_labels,
        'statuses_counts': statuses_counts,
    }
    
    return JsonResponse(data)


# for display years for selection
def get_years(request):
    reports = Report.objects.all()
    years = set()
    
    for report in reports:
        try:
            report_date = datetime.datetime.strptime(report.datetime, '%Y-%m-%d %H:%M:%S')
            years.add(report_date.year)
        except ValueError:
            continue
    
    sorted_years = sorted(years, reverse=True)
    return JsonResponse({'years': sorted_years})


# for displaying report counts
def reports_by_year(request, year):
    reports = Report.objects.filter(datetime__startswith=str(year))
    total_reports = reports.count()
    return JsonResponse({'year': year, 'total_reports': total_reports})

def reports_by_year_month(request, year, month):
    month_str = f"{month:02d}"  # Ensure month is two digits
    date_prefix = f"{year}-{month_str}"
    reports = Report.objects.filter(datetime__startswith=date_prefix)
    total_reports = reports.count()
    return JsonResponse({'year': year, 'month': month, 'total_reports': total_reports})

def reports_by_year_month_date(request, year, month, day):
    month_str = f"{month:02d}"  # Ensure month is two digits
    day_str = f"{day:02d}"      # Ensure day is two digits
    date_prefix = f"{year}-{month_str}-{day_str}"
    reports = Report.objects.filter(datetime__startswith=date_prefix)
    total_reports = reports.count()
    return JsonResponse({'year': year, 'month': month, 'day': day, 'total_reports': total_reports})


def error(request):
    return render(request, 'error.html')

def success(request):
    return render(request, 'success.html')


