from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Username"
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }
        )
    )

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter Password"
            }
        )
    )

    confirm_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm Password"
            }
        )
    )

    def clean_username(self):

        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():

            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():

            raise forms.ValidationError(
                "Email already registered."
            )

        return email

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            if password != confirm_password:

                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

        return cleaned_data