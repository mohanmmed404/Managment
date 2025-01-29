from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View

from customers.forms import ProfileForm, form_validation_error
from customers.models import Profile
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Branch
from .forms import BranchForm,CustomerForm,EditCustomerForm,AddUserProfileForm
from django.contrib.auth.decorators import user_passes_test
from .models import Profile, Branch

from django.core.exceptions import PermissionDenied

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfileView(View):
    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.profile, __ = Profile.objects.get_or_create(user=request.user)
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'profile': self.profile, 'segment': 'profile'}
        return render(request, 'customers/profile.html', context)

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=self.profile)

        if form.is_valid():
            profile = form.save()
            profile.user.first_name = form.cleaned_data.get('first_name')
            profile.user.last_name = form.cleaned_data.get('last_name')
            profile.user.email = form.cleaned_data.get('email')
            profile.user.save()

            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('profile')
@method_decorator(login_required(login_url='login'), name='dispatch')
class TransactionsView(View):
    def get(self, request):
        # Ensure the Profile exists for the current user
        self.profile = Profile.objects.all()
        context = {'profile': self.profile, 'segment': 'transactions'}
        return render(request, 'customers/transactions.html', context)
    


@login_required
def add_user(request):
    """
    Allows userAdmin to create users (customers and editors).
    Allows userEditor to create customers only in their branches.
    """
    if request.user.profile.role not in [Profile.ROLE_USER_ADMIN, Profile.ROLE_USER_EDITOR]:
        raise PermissionDenied()

    # Determine allowed branches
    if request.user.profile.role == Profile.ROLE_USER_EDITOR:
        allowed_branches = request.user.profile.branches.all()
    else:
        allowed_branches = Branch.objects.all()

    if request.method == "POST":
        form = AddUserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check if the username already exists
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    messages.error(request, "A user with this username already exists.")
                    return render(request, "customers/add_new_user.html", {"form": form})

                # Create the User object
                new_user = User.objects.create(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                new_user.set_password("defaultpassword")  # Set a default password
                new_user.save()

                # Create the Profile object
                role = form.cleaned_data['role']
                new_profile = Profile.objects.create(
                    user=new_user,
                    role=role,
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    zip=form.cleaned_data['zip'],
                    avatar=form.cleaned_data.get('avatar'),
                )

                # Assign branches for customers or editors
                if role in [Profile.ROLE_Profile, Profile.ROLE_USER_EDITOR]:
                    if request.user.profile.role == Profile.ROLE_USER_EDITOR:
                        new_profile.branches.set(form.cleaned_data['branches'] & allowed_branches)
                    else:
                        new_profile.branches.set(form.cleaned_data['branches'])

                new_profile.save()
                messages.success(request, "User successfully created.")
                return redirect('customer_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddUserProfileForm()
        form.fields['branches'].queryset = allowed_branches

    return render(request, "customers/add_new_user.html", {"form": form})




@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            message_id = data.get('id')

            if not phone:
                return JsonResponse({'success': False, 'error': 'Phone number is required.'}, status=400)

            # Replace with your external API endpoint
            api_url = "http://respect.com.dedi5536.your-server.de/app/getForm"
            payload = {
                "phone": phone,
                "title": "Transaction Update",
                "body": f"Message for transaction ID {message_id}",
            }
            headers = {'Content-Type': 'application/json'}

            # Send request to external API
            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                messages.success(request, 'Message sent successfully!')

                return JsonResponse({'success': True, 'data': response_data})
            else:
                messages.error(request, 'Invalid email or password.')

                return JsonResponse({'success': False, 'error': response_data.get('error', 'Unknown error')}, status=response.status_code)
        except Exception as e:
            messages.error(request, 'Invalid email or password.')

            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    messages.error(request, 'Invalid email or password.')

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

def check_branch_access(user, branch):
    if user.profile.role == Profile.ROLE_USER_ADMIN:
        return True
    elif user.profile.role == Profile.ROLE_USER_EDITOR:
        return branch in user.profile.branches.all()
    else:
        return False
@login_required
def customer_list(request):
    if request.user.profile.role == Profile.ROLE_USER_ADMIN:
        # Admin sees all customers
        customers = Profile.objects.filter(role=Profile.ROLE_Profile)
    elif request.user.profile.role == Profile.ROLE_USER_EDITOR:
        # Editor sees all profiles (customers and editors) in their assigned branches
        customers = Profile.objects.profiles_for_user(request.user)
    else:
        raise PermissionDenied()

    return render(request, "customers/customer_list.html", {"customers": customers})




@login_required
def manage_branches(request):
    if request.user.profile.role != 'userAdmin':
        return redirect('unauthorized')  # Redirect unauthorized users

    branches = Branch.objects.all()
    return render(request, 'customers/manage_branches.html', {'branches': branches})



@login_required
def add_branch(request):
    if request.user.profile.role != 'userAdmin':
        return redirect('unauthorized')  # Redirect unauthorized users

    if request.method == 'POST':
        form = BranchForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch added successfully!')
            return redirect('manage_branches')
    else:
        form = BranchForm()
    return render(request, 'customers/add_edit_branch.html', {'form': form, 'branch': None})

@login_required
def edit_customer(request, customer_id):
    customer = get_object_or_404(Profile, id=customer_id, role=Profile.ROLE_Profile)

    if request.method == "POST":
        form = EditCustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect to the customer list after saving changes
    else:
        form = EditCustomerForm(instance=customer)

    return render(request, "customers/edit_customer.html", {"form": form})

@login_required
def edit_branch(request, branch_id):
    if request.user.profile.role != 'userAdmin':
        return redirect('unauthorized')  # Redirect unauthorized users

    branch = get_object_or_404(Branch, id=branch_id)
    if request.method == 'POST':
        form = BranchForm(request.POST, request.FILES, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch updated successfully!')
            return redirect('manage_branches')
    else:
        form = BranchForm(instance=branch)
    return render(request, 'customers/add_edit_branch.html', {'form': form, 'branch': branch})





@login_required
def add_customer(request):
    """
    Allows userAdmin to add a customer to any branch.
    Allows userEditor to add a customer only to their assigned branch.
    """
    if request.user.profile.role not in [Profile.ROLE_USER_ADMIN, Profile.ROLE_USER_EDITOR]:
        raise PermissionDenied()

    # Limit branch selection based on user role
    if request.user.profile.role == Profile.ROLE_USER_EDITOR:
        allowed_branches = request.user.profile.branches.all()
    else:
        allowed_branches = Branch.objects.all()

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer_user = User.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email']
            )
            customer = Profile.objects.create(
                user=customer_user,
                role=Profile.ROLE_Profile,
                phone=form.cleaned_data['phone'],
            )
            # Assign branch
            customer.branches.set(form.cleaned_data['branches'] & allowed_branches)
            return redirect("customer_list")
    else:
        form = CustomerForm()
        form.fields['branches'].queryset = allowed_branches  # Limit branch options

    return render(request, "customers/add_customer.html", {"form": form})


def is_user_admin(user):
    return user.profile.role == 'userAdmin'

def is_user_editor(user):
    return user.profile.role == 'userEditor'


@method_decorator(user_passes_test(is_user_admin, login_url='login'), name='dispatch')
class UserAdminView(View):
    def get(self, request):
        profiles = Profile.objects.filter(role__in=['normal', 'userEditor'])
        return render(request, 'customers/transactions.html', {'profiles': profiles})

    def post(self, request):
        # Logic for creating users and assigning roles
        pass


@method_decorator(user_passes_test(is_user_editor, login_url='login'), name='dispatch')
class UserEditorView(View):
    def get(self, request):
        branches = request.user.profile.branches.all()
        return render(request, 'editor/manage_profiles.html', {'branches': branches})

    def post(self, request):
        # Logic for creating users for specific branches
        pass
