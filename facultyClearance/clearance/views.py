from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count
from .forms import UploadForm
from .models import FacultyMember, DepartmentChair, CollegeDean, Requirement, Upload, Department
from django.contrib.auth import get_user_model


User = get_user_model()


from django.conf import settings
print(settings.TEMPLATES)


@login_required
def dashboard(request):
    user = request.user
    role = None
    documents = None
    pending_approvals = None
    requirements = []
    uploads = []
    upload_dict = {}

    # Determine user role
    if hasattr(user, 'facultymember'):
        role = 'part_timer' if user.facultymember.is_part_time else 'faculty'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

    elif hasattr(user, 'departmentchair'):
        role = 'chair'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show pending approvals for faculty under this department
        pending_approvals = Upload.objects.filter(
            uploaded_by__facultymember__department=user.departmentchair.department,
            status='pending'
        ).exclude(uploaded_by=user)

    elif hasattr(user, 'collegedean'):
        role = 'dean'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show pending approvals from department chairs
        pending_approvals = Upload.objects.filter(status='pending').exclude(uploaded_by=user)

    else:
        role = 'unknown'

    # Map each requirement to the user’s uploaded file (if any)
    upload_dict = {upload.requirement.id: upload for upload in uploads}

    print("[DEBUG] User:", user)
    print("[DEBUG] Uploads:", uploads)

    context = {
        'user': user,
        'role': role,
        'requirements': requirements,
        'upload_dict': upload_dict,
        'pending_approvals': pending_approvals,
    }

    return render(request, 'clearance/dashboard.html', context)


@require_POST
@login_required
def inline_upload(request, req_id):
    requirement = get_object_or_404(Requirement, id=req_id)
    user = request.user
    file = request.FILES.get('file')

    if file:
        # Check if there's an existing upload for this user and requirement
        upload, created = Upload.objects.get_or_create(
            uploaded_by=user,
            requirement=requirement,
            defaults={'file': file}
        )
        if not created:
            upload.file = file  # Update file
            upload.status = 'pending'  # Reset status if needed
            upload.save()

    return redirect(f'/clearance/dashboard/?open={req_id}&uploaded=true')


def upload(request, req_id):
    requirement = get_object_or_404(Requirement, id=req_id)
    user = request.user

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.uploaded_by = user
            upload.requirement = requirement
            upload.save()
            return redirect('dashboard')
    else:
        form = UploadForm()

    return render(request, 'clearance/upload_form.html', {
        'form': form,
        'requirement': requirement
    })


def upload_success(request):
    return render(request, 'clearance/upload_success.html')


@login_required
def reupload(request, req_id):
    user = request.user
    upload = get_object_or_404(Upload, uploaded_by=user, requirement_id=req_id)

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, instance=upload)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UploadForm(instance=upload)

    return render(request, 'clearance/upload_form.html', {
        'form': form,
        'requirement': upload.requirement,
        'is_reupload': True  # 💡 Context flag
    })


@login_required
def approvals(request):
    user = request.user
    role = None
    requirements = []
    uploads = []
    pending_approvals = []

    # Check user role
    if hasattr(user, 'facultymember'):
        role = 'part_timer' if user.facultymember.is_part_time else 'faculty'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

    elif hasattr(user, 'departmentchair'):
        role = 'chair'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show pending approvals from faculty in their department, excluding their own uploads
        pending_approvals = Upload.objects.filter(
            uploaded_by__facultymember__department=user.departmentchair.department,
            status='pending'
        ).exclude(uploaded_by=user)

    elif hasattr(user, 'collegedean'):
        role = 'dean'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show all pending faculty uploads across departments (for dean-level approval)
        pending_approvals = Upload.objects.filter(
            status='pending',
            uploaded_by__facultymember__isnull=False
        )

    else:
        role = 'unknown'

    context = {
        'role': role,
        'requirements': requirements,
        'uploads': uploads,
        'pending_approvals': pending_approvals
    }

    return render(request, 'clearance/approvals.html', context)


@login_required
def approve_upload(request, upload_id):
    upload = get_object_or_404(Upload, id=upload_id)
    upload.status = 'Approved'
    upload.save()
    messages.success(request, f"{upload.requirement.title} by {upload.uploaded_by.get_full_name()} approved.")
    return redirect('approvals')


@login_required
def reject_upload(request, upload_id):
    upload = get_object_or_404(Upload, id=upload_id)
    comment = request.POST.get('comment', '').strip()

    upload.status = 'Rejected'
    upload.comment = comment
    upload.save()
    messages.warning(request, f"{upload.requirement.title} by {upload.uploaded_by.get_full_name()} rejected.")
    return redirect('approvals')


@login_required
def submissions(request):
    role = None
    user = request.user
    department_data = []

    # Check user role
    if hasattr(user, 'facultymember'):
        role = 'part_timer' if user.facultymember.is_part_time else 'faculty'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

    elif hasattr(user, 'departmentchair'):
        role = 'chair'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show pending approvals from faculty in their department, excluding their own uploads
        pending_approvals = Upload.objects.filter(
            uploaded_by__facultymember__department=user.departmentchair.department,
            status='pending'
        ).exclude(uploaded_by=user)

    elif hasattr(user, 'collegedean'):
        role = 'dean'
        requirements = Requirement.objects.filter(applicable_to=role)
        uploads = Upload.objects.filter(uploaded_by=user)

        # Show all pending faculty uploads across departments (for dean-level approval)
        pending_approvals = Upload.objects.filter(
            status='pending',
            uploaded_by__facultymember__isnull=False
        )

    else:
        role = 'unknown'

    if hasattr(user, 'collegedean'):
        departments = Department.objects.all()
    elif hasattr(user, 'departmentchair'):
        departments = Department.objects.filter(id=user.departmentchair.department.id)
    else:
        return render(request, 'unauthorized.html', {
            'message': "You are not authorized to view faculty submissions."
        })

    for dept in departments:
        chair = getattr(dept, 'departmentchair', None)
        faculty_members = User.objects.filter(facultymember__department=dept)
        uploads = Upload.objects.filter(
            uploaded_by__in=faculty_members
        ).select_related('uploaded_by', 'requirement')

        # Group by faculty
        faculty_data = []
        for faculty in faculty_members:
            user_uploads = uploads.filter(uploaded_by=faculty)
            total_reqs = Requirement.objects.count()
            approved_count = user_uploads.filter(status='Approved').count()

            faculty_data.append({
                'user': faculty,
                'uploads': user_uploads,
                'is_complete': approved_count == total_reqs and total_reqs > 0
            })

        complete = sum(1 for f in faculty_data if f['is_complete'])
        total = faculty_members.count()
        incomplete = total - complete
        percent_complete = round((complete / total) * 100) if total > 0 else 0
        has_incomplete = complete < total

        department_data.append({
            'name': dept.name,
            'chair': chair.user if chair else None,
            'faculty_data': faculty_data,
            'percent_complete': percent_complete,
            'complete': complete,
            'total': total,
            'incomplete': incomplete,
            'has_incomplete': has_incomplete
        })

    return render(request, 'clearance/submissions.html', {
        'department_data': department_data,
        'role': role,
    })

