from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, Expense, Budget, Income
from .forms import UserForm, ExpenseForm, BudgetForm, ReportForm, IncomeForm
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from datetime import timedelta

from datetime import date

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Sum

import openpyxl

def index(request):
    return render(request, 'index.html')

def create_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Hash the password before saving 
            user.Password = make_password(form.cleaned_data['Password'])
            user.save()

            messages.success(request, "Account created successfully. Please login.")
            return redirect('login')   # redirect to the login page
    else:
        form = UserForm()

    return render(request, 'create_user.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(Email=email)

            # Check password hash
            if check_password(password, user.Password):
                # You can store session here
                request.session['user_id'] = user.id
                request.session['user_name'] = user.FullName

                return redirect('dashboard')  # Change to your dashboard/home
            else:
                messages.error(request, "Invalid password")

        except User.DoesNotExist:
            messages.error(request, "No account found with that email")

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')

def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = UserForm(request.POST or None, instance=user)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # or any page you prefer

    return render(request, 'update_user.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        request.session.flush()  # logout if deleting current user
        return redirect('create_user')

    return render(request, 'delete_user_confirm.html', {'user': user})


def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    budget = Budget.objects.filter(UserId_id=user_id).first()
    
    total_income = Income.objects.filter(UserId_id=user_id).aggregate(Sum('Amount'))['Amount__sum'] or 0
    total_expense = sum(float(exp.ExpenseCost) for exp in Expense.objects.filter(UserId_id=user_id))

    balance = total_income - total_expense

    alert = None
    remaining = None

    if budget:
        total = calculate_expense_total(user_id, budget.Period)

        if total > budget.Amount:
            alert = f"⚠️ You have exceeded your {budget.Period} budget!"
        else:
            remaining = budget.Amount - total

    return render(request, 'dashboard.html', {
        'alert': alert,
        'remaining': remaining,
        'budget': budget,
        'user_name': request.session['user_name'],
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    })



# Expense creation
def create_expense(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.UserId_id = request.session['user_id']   # auto assign user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'create_expense.html', {'form': form})


def expense_list(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    expenses = Expense.objects.filter(UserId_id=user_id).order_by('-ExpenseDate')

    return render(request, 'expense_list.html', {'expenses': expenses})


def edit_expense(request, expense_id):
    if 'user_id' not in request.session:
        return redirect('login')

    # Get the expense that belongs to the logged-in user only
    expense = get_object_or_404(Expense, id=expense_id, UserId_id=request.session['user_id'])

    form = ExpenseForm(request.POST or None, instance=expense)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('expense_list')

    return render(request, 'edit_expense.html', {'form': form, 'expense': expense})

def delete_expense(request, expense_id):
    if 'user_id' not in request.session:
        return redirect('login')

    expense = get_object_or_404(Expense, id=expense_id, UserId_id=request.session['user_id'])

    if request.method == "POST":
        expense.delete()
        return redirect('expense_list')

    return render(request, 'delete_expense_confirm.html', {'expense': expense})

# budget views
def budget(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    # If budget exists, edit it instead of creating duplicate
    budget = Budget.objects.filter(UserId_id=user_id).first()

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.UserId_id = user_id
            obj.save()
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'budget.html', {'form': form, 'budget': budget})

def calculate_expense_total(user_id, period):
    today = timezone.now().date()

    if period == "daily":
        start = today
    elif period == "weekly":
        start = today - timedelta(days=today.weekday())
    elif period == "monthly":
        start = today.replace(day=1)
    elif period == "yearly":
        start = today.replace(month=1, day=1)
    else:
        return 0

    # Fetch expenses from start date
    expenses = Expense.objects.filter(
        UserId_id=user_id,
        ExpenseDate__gte=start
    )

    total = sum(float(exp.ExpenseCost) for exp in expenses)
    return total


# reports

def filter_expenses(user_id, report_type, selected_date):
    if report_type == 'daily':
        return Expense.objects.filter(
            UserId_id=user_id,
            ExpenseDate=selected_date
        )

    elif report_type == 'monthly':
        return Expense.objects.filter(
            UserId_id=user_id,
            ExpenseDate__year=selected_date.year,
            ExpenseDate__month=selected_date.month
        )

    elif report_type == 'yearly':
        return Expense.objects.filter(
            UserId_id=user_id,
            ExpenseDate__year=selected_date.year
        )

    return Expense.objects.none()


def expense_report(request):
    if 'user_id' not in request.session:
        return redirect('login')

    report_data = None
    total = 0

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            selected_date = form.cleaned_data['date']

            report_data = filter_expenses(
                request.session['user_id'],
                report_type,
                selected_date
            )

            total = sum(float(exp.ExpenseCost) for exp in report_data)

            return render(request, 'report.html', {
                'form': form,
                'report_data': report_data,
                'total': total,
                'report_type': report_type,
                'selected_date': selected_date,
            })
    else:
        form = ReportForm()

    return render(request, 'report.html', {'form': form})


def download_excel(request, report_type, year, month, day):
    selected_date = date(year, month, day)
    user_id = request.session['user_id']

    expenses = filter_expenses(user_id, report_type, selected_date)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Expense Report"

    sheet.append(["Date", "Item", "Cost"])

    for exp in expenses:
        sheet.append([str(exp.ExpenseDate), exp.ExpenseItem, exp.ExpenseCost])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="expense_report.xlsx"'
    workbook.save(response)

    return response



def download_pdf(request, report_type, year, month, day):
    selected_date = date(year, month, day)
    user_id = request.session['user_id']

    expenses = filter_expenses(user_id, report_type, selected_date)
    total = sum(float(exp.ExpenseCost) for exp in expenses)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Expense Report: {report_type.upper()}")

    y = 760
    for exp in expenses:
        p.drawString(100, y, f"{exp.ExpenseDate} - {exp.ExpenseItem} - ₹{exp.ExpenseCost}")
        y -= 20

    p.drawString(100, y - 20, f"Total: ₹{total}")
    p.showPage()
    p.save()

    return response





# charts

from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime

def expense_chart_data(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user_id = request.session['user_id']
    today = datetime.today()

    # Group expenses by day for the current month
    expenses = (
        Expense.objects.filter(
            UserId_id=user_id,
            ExpenseDate__year=today.year,
            ExpenseDate__month=today.month
        )
        .values('ExpenseDate')
        .annotate(total=Sum('ExpenseCost'))
        .order_by('ExpenseDate')
    )

    labels = [str(exp['ExpenseDate']) for exp in expenses]
    data = [float(exp['total']) for exp in expenses]

    return JsonResponse({
        "labels": labels,
        "data": data
    })



def budget_vs_expense_data(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user_id = request.session['user_id']
    today = datetime.today()

    budget = Budget.objects.filter(UserId_id=user_id).first()
    if not budget:
        return JsonResponse({'labels': [], 'data': []})

    # get total spent in selected budget period
    total = calculate_expense_total(user_id, budget.Period)

    remaining = max(budget.Amount - total, 0)

    return JsonResponse({
        "labels": ["Spent", "Remaining"],
        "data": [total, remaining]
    })


def expense_chart_data_filtered(request, period):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user_id = request.session['user_id']
    today = date.today()

    if period == "weekly":
        start_date = today - timedelta(days=today.weekday())
    elif period == "monthly":
        start_date = today.replace(day=1)
    elif period == "yearly":
        start_date = today.replace(month=1, day=1)
    else:
        return JsonResponse({'labels': [], 'data': []})

    expenses = (
        Expense.objects.filter(
            UserId_id=user_id,
            ExpenseDate__gte=start_date
        )
        .values('ExpenseDate')
        .annotate(total=Sum('ExpenseCost'))
        .order_by('ExpenseDate')
    )

    labels = [str(exp['ExpenseDate']) for exp in expenses]
    data = [float(exp['total']) for exp in expenses]

    return JsonResponse({"labels": labels, "data": data})


def category_chart_data(request):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user_id = request.session['user_id']

    expenses = (
        Expense.objects.filter(UserId_id=user_id)
        .values('Category')
        .annotate(total=Sum('ExpenseCost'))
    )

    labels = [exp['Category'] for exp in expenses]
    data = [float(exp['total']) for exp in expenses]

    return JsonResponse({"labels": labels, "data": data})

#income

def create_income(request):
    if 'user_id' not in request.session:
        return redirect('login')

    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.UserId_id = request.session['user_id']
            income.save()
            return redirect('income_list')
    else:
        form = IncomeForm()

    return render(request, 'create_income.html', {'form': form})


def income_list(request):
    if 'user_id' not in request.session:
        return redirect('login')

    incomes = Income.objects.filter(UserId_id=request.session['user_id']).order_by('-IncomeDate')
    return render(request, 'income_list.html', {'incomes': incomes})


def edit_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, UserId_id=request.session['user_id'])
    form = IncomeForm(request.POST or None, instance=income)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('income_list')

    return render(request, 'edit_income.html', {'form': form, 'income': income})


def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, UserId_id=request.session['user_id'])

    if request.method == "POST":
        income.delete()
        return redirect('income_list')

    return render(request, 'delete_income_confirm.html', {'income': income})
