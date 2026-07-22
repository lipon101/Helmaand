from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegisterForm, ProfileUpdateForm
from .models import Profile
from security.ctf_flags import (
    CSRF_POST, CSRF_GET, CSRF_LOGIN, CSRF_LOGOUT, CSRF_PASSWORD,
    XSS_SELF,
)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Profile.objects.create(user=user)
            messages.success(request, f"Account created for {user.username}! You can now log in.")
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('shop:home')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('shop:home')


@login_required
def profile_view(request):
    """
    VULNERABLE (XSS - Self): The profile page renders the logged-in user's
    username with |safe and sets a flag cookie. A user who registers with a
    username containing an XSS payload will execute JS on their own profile.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('accounts:profile')
    else:
        p_form = ProfileUpdateForm(instance=profile)

    response = render(request, 'accounts/profile.html', {
        'p_form': p_form,
    })
    # CTF: flag cookie — exfiltrate via Self-XSS (document.cookie)
    response.set_cookie('ctf_xss_self', XSS_SELF)
    return response


@csrf_exempt
@login_required
def change_email_view(request):
    """
    VULNERABLE (CSRF - POST state change): @csrf_exempt disables Django's CSRF
    protection on this state-changing POST endpoint. A malicious page can
    submit a cross-site form POST here to silently change the logged-in user's
    email.
    """
    if request.method == 'POST':
        new_email = request.POST.get('email', '').strip()
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, "Your email has been updated successfully!")
            # CTF: flag revealed — CSRF POST succeeded
            messages.info(request, f"Flag: {CSRF_POST}")
            return redirect('accounts:profile')
        messages.error(request, "Email field cannot be empty.")
    return render(request, 'accounts/change_email.html')


@login_required
def reset_preferences_view(request):
    """
    VULNERABLE (CSRF - GET state change): This endpoint performs a
    state-changing operation (resetting the user's profile shipping info)
    via a simple GET request — no CSRF token, no POST required. A victim
    only needs to visit a crafted link like:
        <img src="https://helmaand.local/accounts/reset-preferences/">
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.phone = ''
    profile.address = ''
    profile.city = ''
    profile.postal_code = ''
    profile.save()
    messages.warning(request, "Your shipping preferences have been reset.")
    # CTF: flag revealed — CSRF GET succeeded
    messages.info(request, f"Flag: {CSRF_GET}")
    return redirect('accounts:profile')


@csrf_exempt
def quick_login_view(request):
    """
    VULNERABLE (CSRF - Login CSRF): The login form has no CSRF token and the
    view is @csrf_exempt, so an attacker can forge a cross-site login request.
    The attacker logs the victim into the attacker's own account (e.g., to
    plant data or exploit trust features that appear only when "logged in").
    """
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f"Welcome back, {username}!")
            # CTF: flag revealed — Login CSRF succeeded
            messages.success(request, f"Flag: {CSRF_LOGIN}")
            return redirect('shop:home')
        messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/quick_login.html')


@login_required
def force_logout_view(request):
    """
    VULNERABLE (CSRF - Logout via GET): Logs out the current user on a plain
    GET request with no CSRF protection. A victim can be forcibly logged out
    by visiting a crafted link or an <img> tag pointing here.
    """
    logout(request)
    messages.warning(request, "You have been forcibly logged out.")
    # CTF: flag revealed — Logout CSRF succeeded
    messages.info(request, f"Flag: {CSRF_LOGOUT}")
    return redirect('accounts:login')


@csrf_exempt
@login_required
def change_password_view(request):
    """
    VULNERABLE (CSRF - Password change): @csrf_exempt disables CSRF protection
    on this state-changing POST endpoint. An attacker can forge a cross-site
    POST to change the victim's password to a known value.
    """
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            # Keep the session alive after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password has been changed successfully!")
            # CTF: flag revealed — CSRF password change succeeded
            messages.info(request, f"Flag: {CSRF_PASSWORD}")
            return redirect('accounts:profile')
        messages.error(request, "Password field cannot be empty.")
    return render(request, 'accounts/change_password.html')
