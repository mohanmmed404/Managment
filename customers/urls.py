from django.urls import path
from customers import views

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
        path('transAction/', views.TransactionsView.as_view(), name='transAction'),
    path('send-message/', views.send_message, name='send_message'),
    path('branches/manage/', views.manage_branches, name='manage_branches'),
    path('branches/add/', views.add_branch, name='add_branch'),
    path('branches/edit/<int:branch_id>/', views.edit_branch, name='edit_branch'),  # Ensure this exists
   path('customers/', views.customer_list, name='customer_list'),  # View all customers
    path('customers/add/', views.add_customer, name='add_customer'),  # Add a new customer
    path('customers/edit/<int:customer_id>/', views.edit_customer, name='edit_customer'),  # Edit customer

    # User management views (for userAdmin)
    path('users/add/', views.add_user, name='add_user'),  # Add new user (admin/editor)

]
