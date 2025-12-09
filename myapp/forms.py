from django import forms
from .models import User, Expense, Budget, Income

class UserForm(forms.ModelForm):
    Password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['FullName', 'Email', 'Password']


class ExpenseForm(forms.ModelForm):
    ExpenseDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Expense
        fields = ['ExpenseDate', 'Category', 'ExpenseItem', 'ExpenseCost']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['Period', 'Amount']


class ReportForm(forms.Form):
    REPORT_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    report_type = forms.ChoiceField(choices=REPORT_CHOICES)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))



class IncomeForm(forms.ModelForm):
    IncomeDate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d']
    )

    class Meta:
        model = Income
        fields = ['IncomeDate', 'Category', 'Source', 'Amount']

