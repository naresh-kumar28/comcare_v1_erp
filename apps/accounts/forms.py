from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.accounts.models import CustomUser


class UserRegisterForm(UserCreationForm):
    """
    Custom user registration form for CustomUser model where email is the USERNAME_FIELD.
    Inherits from Django's built-in UserCreationForm.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@example.com',
            'class': 'w-full px-4 py-3 bg-[var(--color-background)] border border-gray-200 focus:border-[var(--color-primary)] focus:bg-white rounded-xl font-medium outline-none transition',
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'w-full px-4 py-3 bg-[var(--color-background)] border border-gray-200 focus:border-[var(--color-primary)] focus:bg-white rounded-xl font-medium outline-none transition',
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'w-full px-4 py-3 bg-[var(--color-background)] border border-gray-200 focus:border-[var(--color-primary)] focus:bg-white rounded-xl font-medium outline-none transition',
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '10-digit mobile number',
            'class': 'w-full px-4 py-3 bg-[var(--color-background)] border border-gray-200 focus:border-[var(--color-primary)] focus:bg-white rounded-xl font-medium outline-none transition',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '').strip().lower()
        # CustomUser uses email as username
        user.username = user.email
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form for admin panel or profile editing.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'profile_picture')
