from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('create-user', views.create_user, name='create_user'),
    path('login/', views.login_view, name='login'),
    
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    path('user/<int:user_id>/update/', views.update_user, name='update_user'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),

    path('expenses/create/', views.create_expense, name='create_expense'),
    path('expenses/', views.expense_list, name='expense_list'),

    path('expense/<int:expense_id>/edit/', views.edit_expense, name='edit_expense'),
    path('expense/<int:expense_id>/delete/', views.delete_expense, name='delete_expense'),

    path('budget/', views.budget, name='budget'),

    path('report/', views.expense_report, name='expense_report'),

    path('report/pdf/<str:report_type>/<int:year>/<int:month>/<int:day>/',
     views.download_pdf, name='download_pdf'),

    path('report/excel/<str:report_type>/<int:year>/<int:month>/<int:day>/',
     views.download_excel, name='download_excel'),

    path('chart-data/', views.expense_chart_data, name='expense_chart_data'),

    path('chart-budget/', views.budget_vs_expense_data, name='budget_vs_expense_data'),

    path('chart-data/<str:period>/', views.expense_chart_data_filtered, name='expense_chart_data_filtered'),

    path('chart-category/', views.category_chart_data, name='category_chart_data'),


    #income urls
    path('income/add/', views.create_income, name='create_income'),
    path('income/', views.income_list, name='income_list'),
    path('income/<int:income_id>/edit/', views.edit_income, name='edit_income'),
    path('income/<int:income_id>/delete/', views.delete_income, name='delete_income'),
]