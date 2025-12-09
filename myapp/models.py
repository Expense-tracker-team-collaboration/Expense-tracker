from django.db import models

class User(models.Model):
    FullName = models.CharField(max_length=100)
    Email = models.EmailField(max_length=100,unique=True)
    Password = models.CharField(max_length=50)
    RegDate = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('entertainment', 'Entertainment'),
        ('health', 'Health'),
        ('other', 'Other'),
    )
    UserId = models.ForeignKey(User,on_delete=models.CASCADE)
    ExpenseDate = models.DateField(null=True,blank=True)
    ExpenseItem = models.CharField(max_length=100)
    ExpenseCost = models.CharField(max_length=100)
    Category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    NotDate = models.DateTimeField(auto_now_add=True)

class Budget(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    Amount = models.FloatField()
    CreatedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.UserId.FullName} - {self.Period} Budget"


class Income(models.Model):
    CATEGORY_CHOICES = (
        ('salary', 'Salary'),
        ('business', 'Business'),
        ('freelance', 'Freelance'),
        ('gift', 'Gift'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    )

    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    IncomeDate = models.DateField(null=True, blank=True)
    Category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    Source = models.CharField(max_length=100)
    Amount = models.FloatField()
    NotDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Source} - {self.Amount}"
