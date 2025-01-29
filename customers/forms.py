from django import forms

from customers.models import Profile

from django import forms
from .models import Branch

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']


def form_validation_error(form):
    msg = ""
    for field in form:
        for error in field.errors:
            msg += "%s: %s \\n" % (field.label if hasattr(field, 'label') else 'Error', error)
    return msg


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'picture']

class CustomerForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=32, label="Phone")
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.none(),  # Dynamically set in the view
        widget=forms.CheckboxSelectMultiple,
        label="Branches"
    )


from django import forms
from .models import Profile
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class EditCustomerForm(forms.ModelForm):
    # Add User-related fields
    first_name = forms.CharField(max_length=150, label="First Name")
    last_name = forms.CharField(max_length=150, label="Last Name")
    email = forms.EmailField(label="Email")

    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'zip', 'branches', 'avatar']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.pop('user_instance', None)  # Pass user instance to form
        super().__init__(*args, **kwargs)

        # Prepopulate User fields if user_instance is provided
        if user_instance:
            self.fields['first_name'].initial = user_instance.first_name
            self.fields['last_name'].initial = user_instance.last_name
            self.fields['email'].initial = user_instance.email

        # Customize field widgets if needed
        self.fields['branches'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        # Save User-related fields
        user_instance = self.instance.user
        user_instance.first_name = self.cleaned_data['first_name']
        user_instance.last_name = self.cleaned_data['last_name']
        user_instance.email = self.cleaned_data['email']

        if commit:
            user_instance.save()
            super().save(commit=commit)
        return self.instance


from django import forms
from .models import Branch

class AddCustomerForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=32, label="Phone", widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, label="Address", widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=50, label="City", widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip = forms.CharField(max_length=30, label="ZIP Code", widget=forms.TextInput(attrs={'class': 'form-control'}))
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Branches"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branches'].queryset = Branch.objects.none()  # Default to no branches

from django import forms
from .models import Branch, Profile

class AddUserProfileForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, label="First Name", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, label="Last Name", widget=forms.TextInput(attrs={'class': 'form-control'}))

    # Profile fields
    phone = forms.CharField(max_length=32, label="Phone", widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=255, label="Address", widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=50, label="City", widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip = forms.CharField(max_length=30, label="ZIP Code", widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
        choices=[
            (Profile.ROLE_Profile, "Customer"),
            (Profile.ROLE_USER_EDITOR, "Editor")
        ],
        label="Role",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Branches"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branches'].queryset = Branch.objects.none()  # Dynamically set in the view
