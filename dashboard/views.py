from django.shortcuts import render

# No reverse(), no redirects, just the function
def admin_dashboard(request):
    return render(request, 'dashboard/index.html')
