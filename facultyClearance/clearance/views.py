from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ClearanceDocumentForm
from .models import ClearanceDocument, FacultyMember, DepartmentChair, CollegeDean


from django.conf import settings
print(settings.TEMPLATES)


@login_required
def dashboard(request):
    user = request.user
    role = None
    documents = None
    pending_approvals = None

    try:
        faculty = FacultyMember.objects.get(user=user)
        role = 'Faculty Member'
        documents = ClearanceDocument.objects.filter(uploader=user)
    except FacultyMember.DoesNotExist:
        try:
            chair = DepartmentChair.objects.get(user=user)
            role = 'Department Chair'
            # Approvals needed for faculty in this department
            pending_approvals = ClearanceDocument.objects.filter(
                department=chair.department,
                role='faculty',
                is_approved=False
            )
        except DepartmentChair.DoesNotExist:
            try:
                dean = CollegeDean.objects.get(user=user)
                role = 'College Dean'
                # Approvals needed for department chairs
                pending_approvals = ClearanceDocument.objects.filter(
                    role='chair',
                    is_approved=False
                )
            except CollegeDean.DoesNotExist:
                role = 'Unknown'

    context = {
        'user': user,
        'role': role,
        'documents': documents,
        'pending_approvals': pending_approvals
    }

    return render(request, 'clearance/dashboard.html', context)


def upload_clearance_document(request):
    user = request.user
    role = 'faculty'
    department = None

    # Identify the user's role and department
    try:
        profile = FacultyMember.objects.get(user=user)
        department = profile.department
        role = 'faculty'
    except FacultyMember.DoesNotExist:
        try:
            profile = DepartmentChair.objects.get(user=user)
            department = profile.department
            role = 'chair'
        except DepartmentChair.DoesNotExist:
            return render(request, 'clearance/access_denied.html')

    if request.method == 'POST':
        form = ClearanceDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploader = user
            doc.role = role
            doc.department = department
            doc.save()
            return redirect('upload_success')
    else:
        form = ClearanceDocumentForm()

    return render(request, 'clearance/upload_form.html', {'form': form})


def upload_success(request):
    return render(request, 'clearance/upload_success.html')