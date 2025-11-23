from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
import uuid
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import cloudinary.uploader

from .models import (
    User, GroupMember, ProfessionalCertification, Course,
    Module, ModuleProgress, CourseCertificate,
    ProfessionalCertificationCertificate, CertificationEnrollment
)


def home(request):
    """Homepage with project details and group members"""
    group_members = GroupMember.objects.all().select_related('user')
    certifications = ProfessionalCertification.objects.filter(is_active=True)[:3]

    context = {
        'group_members': group_members,
        'certifications': certifications,
    }
    return render(request, 'courses/home.html', context)


def register(request):
    """User registration with auto-login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        matric_number = request.POST.get('matric_number', '')

        # Validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'courses/register.html')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'courses/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'courses/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'courses/register.html')

        if matric_number and User.objects.filter(matric_number=matric_number).exists():
            messages.error(request, 'Matric number already exists.')
            return render(request, 'courses/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            matric_number=matric_number or None
        )

        # Auto-login
        login(request, user)
        messages.success(request, 'Account created successfully! Welcome to the platform.')
        return redirect('dashboard')

    return render(request, 'courses/register.html')


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'courses/login.html')


@login_required
def user_logout(request):
    """User logout"""
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """User dashboard showing certifications and progress"""
    certifications = ProfessionalCertification.objects.filter(is_active=True).prefetch_related('courses')

    # Get user's progress for each certification
    certification_data = []
    for cert in certifications:
        progress = cert.get_user_progress(request.user)
        is_completed = cert.is_completed_by_user(request.user)

        certification_data.append({
            'certification': cert,
            'progress': progress,
            'is_completed': is_completed,
            'total_courses': cert.get_total_courses()
        })

    # Get recent activity
    recent_progress = ModuleProgress.objects.filter(
        user=request.user
    ).select_related('module', 'module__course').order_by('-last_accessed')[:5]

    # Get certificates
    course_certificates = CourseCertificate.objects.filter(user=request.user).select_related('course')
    professional_certificates = ProfessionalCertificationCertificate.objects.filter(
        user=request.user
    ).select_related('certification')

    context = {
        'certification_data': certification_data,
        'recent_progress': recent_progress,
        'course_certificates': course_certificates,
        'professional_certificates': professional_certificates,
    }
    return render(request, 'courses/dashboard.html', context)


@login_required
def certification_detail(request, pk):
    """Detail view of a professional certification"""
    certification = get_object_or_404(ProfessionalCertification, pk=pk, is_active=True)
    courses = certification.courses.filter(is_active=True).prefetch_related('modules')

    # Get progress for each course
    course_data = []
    for course in courses:
        progress = course.get_user_progress(request.user)
        is_completed = course.is_completed_by_user(request.user)

        course_data.append({
            'course': course,
            'progress': progress,
            'is_completed': is_completed,
            'total_modules': course.get_total_modules()
        })

    overall_progress = certification.get_user_progress(request.user)
    is_certification_complete = certification.is_completed_by_user(request.user)

    # Check if professional certificate exists
    professional_certificate = None
    if is_certification_complete:
        professional_certificate, created = ProfessionalCertificationCertificate.objects.get_or_create(
            user=request.user,
            certification=certification,
            defaults={'certificate_id': f'PROF-{uuid.uuid4().hex[:12].upper()}'}
        )

    context = {
        'certification': certification,
        'course_data': course_data,
        'overall_progress': overall_progress,
        'is_certification_complete': is_certification_complete,
        'professional_certificate': professional_certificate,
    }
    return render(request, 'courses/certification_detail.html', context)


@login_required
def course_detail(request, pk):
    """Detail view of a course"""
    course = get_object_or_404(Course, pk=pk, is_active=True)
    modules = course.modules.filter(is_active=True)

    # Get progress for each module
    module_data = []
    for module in modules:
        try:
            progress = ModuleProgress.objects.get(user=request.user, module=module)
        except ModuleProgress.DoesNotExist:
            progress = None

        module_data.append({
            'module': module,
            'progress': progress,
            'is_completed': progress.is_completed if progress else False
        })

    course_progress = course.get_user_progress(request.user)
    is_course_complete = course.is_completed_by_user(request.user)

    # Check if course certificate exists
    course_certificate = None
    show_confetti = False
    if is_course_complete:
        course_certificate, created = CourseCertificate.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'certificate_id': f'CERT-{uuid.uuid4().hex[:12].upper()}'}
        )
        if created:
            show_confetti = True

    context = {
        'course': course,
        'module_data': module_data,
        'course_progress': course_progress,
        'is_course_complete': is_course_complete,
        'course_certificate': course_certificate,
        'show_confetti': show_confetti,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def module_view(request, pk):
    """View a specific module"""
    module = get_object_or_404(Module, pk=pk, is_active=True)

    # Get or create progress
    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    # Get next and previous modules
    all_modules = module.course.modules.filter(is_active=True).order_by('order')
    current_index = list(all_modules).index(module)

    next_module = all_modules[current_index + 1] if current_index < len(all_modules) - 1 else None
    prev_module = all_modules[current_index - 1] if current_index > 0 else None

    context = {
        'module': module,
        'progress': progress,
        'next_module': next_module,
        'prev_module': prev_module,
        'course': module.course,
    }
    return render(request, 'courses/module_view.html', context)


@login_required
@require_POST
def mark_module_complete(request, pk):
    """Mark a text/picture module as complete (AJAX)"""
    module = get_object_or_404(Module, pk=pk)

    # Only allow for text and picture modules
    if module.module_type not in ['text', 'picture', 'text_picture']:
        return JsonResponse({'success': False, 'error': 'Invalid module type'}, status=400)

    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    if not progress.is_completed:
        progress.mark_as_completed()

    # Check course completion
    course_progress = module.course.get_user_progress(request.user)
    is_course_complete = module.course.is_completed_by_user(request.user)

    return JsonResponse({
        'success': True,
        'is_completed': progress.is_completed,
        'course_progress': course_progress,
        'is_course_complete': is_course_complete
    })


@login_required
@require_POST
def update_video_progress(request, pk):
    """Update video watch progress (AJAX)"""
    module = get_object_or_404(Module, pk=pk)

    if module.module_type != 'video':
        return JsonResponse({'success': False, 'error': 'Invalid module type'}, status=400)

    watch_time = int(request.POST.get('watch_time', 0))

    progress, created = ModuleProgress.objects.get_or_create(
        user=request.user,
        module=module
    )

    progress.update_video_progress(watch_time)

    # Check course completion
    course_progress = module.course.get_user_progress(request.user)
    is_course_complete = module.course.is_completed_by_user(request.user)

    return JsonResponse({
        'success': True,
        'is_completed': progress.is_completed,
        'progress_percentage': progress.get_progress_percentage(),
        'course_progress': course_progress,
        'is_course_complete': is_course_complete
    })


@login_required
def download_course_certificate(request, pk):
    """Generate and download course certificate"""
    certificate = get_object_or_404(CourseCertificate, pk=pk, user=request.user)

    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Draw border
    c.setStrokeColor(colors.HexColor('#2563eb'))
    c.setLineWidth(3)
    c.rect(40, 40, width - 80, height - 80)

    # Title
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.HexColor('#1e40af'))
    c.drawCentredString(width / 2, height - 120, "Certificate of Completion")

    # Decorative line
    c.setStrokeColor(colors.HexColor('#60a5fa'))
    c.setLineWidth(2)
    c.line(150, height - 140, width - 150, height - 140)

    # Body text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 200, "This is to certify that")

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor('#1e40af'))
    c.drawCentredString(width / 2, height - 250, certificate.user.get_full_name())

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 300, "has successfully completed the course")

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor('#1e40af'))

    # Wrap long course titles
    course_title = certificate.course.title
    if len(course_title) > 50:
        words = course_title.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 50:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y_pos = height - 350
        for line in lines:
            c.drawCentredString(width / 2, y_pos, line)
            y_pos -= 30
    else:
        c.drawCentredString(width / 2, height - 350, course_title)

    # Date and certificate ID
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor('#6b7280'))
    c.drawCentredString(width / 2, 150, f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}")
    c.drawCentredString(width / 2, 130, f"Certificate ID: {certificate.certificate_id}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 80, "Learning Platform - Excellence in Education")

    c.save()

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'

    return response


@login_required
def download_professional_certificate(request, pk):
    """Generate and download professional certification certificate"""
    certificate = get_object_or_404(ProfessionalCertificationCertificate, pk=pk, user=request.user)

    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Draw border
    c.setStrokeColor(colors.HexColor('#059669'))
    c.setLineWidth(4)
    c.rect(40, 40, width - 80, height - 80)

    # Inner border
    c.setStrokeColor(colors.HexColor('#10b981'))
    c.setLineWidth(2)
    c.rect(50, 50, width - 100, height - 100)

    # Title
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor('#065f46'))
    c.drawCentredString(width / 2, height - 100, "Professional Certification")

    # Decorative line
    c.setStrokeColor(colors.HexColor('#34d399'))
    c.setLineWidth(2)
    c.line(150, height - 120, width - 150, height - 120)

    # Body text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 170, "This is to certify that")

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor('#065f46'))
    c.drawCentredString(width / 2, height - 210, certificate.user.get_full_name())

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 250, "has successfully completed the professional certification")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor('#065f46'))
    c.drawCentredString(width / 2, height - 290, certificate.certification.title)

    # Courses completed
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 330, "Including completion of the following courses:")

    courses = certificate.certification.courses.filter(is_active=True).order_by('order')
    y_pos = height - 370
    c.setFont("Helvetica", 11)

    for i, course in enumerate(courses, 1):
        if y_pos < 200:  # Prevent overflow
            break
        c.drawCentredString(width / 2, y_pos, f"{i}. {course.title}")
        y_pos -= 20

    # Date and certificate ID
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor('#6b7280'))
    c.drawCentredString(width / 2, 130, f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}")
    c.drawCentredString(width / 2, 110, f"Certificate ID: {certificate.certificate_id}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 70, "Learning Platform - Professional Excellence")

    c.save()

    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="professional_certificate_{certificate.certificate_id}.pdf"'

    return response

# =====================================
# USER PROFILE MANAGEMENT VIEWS
# =====================================

@login_required
def profile(request):
    """User profile view and edit"""
    if request.method == 'POST':
        # Update profile
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        matric_number = request.POST.get('matric_number', '')
        title = request.POST.get('title', '')
        bio = request.POST.get('bio', '')

        # Update user fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.matric_number = matric_number or None
        request.user.title = title
        request.user.bio = bio

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']

        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'user': request.user,
    }
    return render(request, 'courses/profile.html', context)


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Validate old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        # Validate new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')

        # Update password
        request.user.set_password(new_password)
        request.user.save()

        # Re-authenticate user
        login(request, request.user)

        messages.success(request, 'Password changed successfully!')
        return redirect('profile')

    return render(request, 'courses/change_password.html')


# =====================================
# INSTRUCTOR: COURSE MANAGEMENT VIEWS
# =====================================

@login_required
def instructor_dashboard(request):
    """Dashboard for instructors to manage their courses"""
    if not request.user.can_create_courses():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Get instructor's certifications and courses
    certifications = ProfessionalCertification.objects.filter(
        created_by=request.user
    ).annotate(
        course_count=Count('courses')
    )

    courses = Course.objects.filter(created_by=request.user).select_related('certification')

    context = {
        'certifications': certifications,
        'courses': courses,
    }
    return render(request, 'courses/instructor/dashboard.html', context)


@login_required
def create_certification(request):
    """Create a new professional certification or specialization"""
    if not request.user.can_create_courses():
        messages.error(request, 'You do not have permission to create certifications.')
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        certification_type = request.POST.get('certification_type')
        thumbnail = request.FILES.get('thumbnail')

        # Create certification
        certification = ProfessionalCertification.objects.create(
            title=title,
            description=description,
            certification_type=certification_type,
            created_by=request.user,
            thumbnail=thumbnail
        )

        messages.success(request, f'Certification "{title}" created successfully!')
        return redirect('edit_certification', pk=certification.pk)

    return render(request, 'courses/instructor/create_certification.html')


@login_required
def edit_certification(request, pk):
    """Edit an existing certification"""
    certification = get_object_or_404(ProfessionalCertification, pk=pk, created_by=request.user)

    if request.method == 'POST':
        certification.title = request.POST.get('title')
        certification.description = request.POST.get('description')
        certification.certification_type = request.POST.get('certification_type')

        if 'thumbnail' in request.FILES:
            certification.thumbnail = request.FILES['thumbnail']

        certification.save()

        messages.success(request, 'Certification updated successfully!')
        return redirect('edit_certification', pk=pk)

    # Get courses in this certification
    courses = certification.courses.all().order_by('order')

    context = {
        'certification': certification,
        'courses': courses,
    }
    return render(request, 'courses/instructor/edit_certification.html', context)


@login_required
def delete_certification(request, pk):
    """Delete a certification"""
    certification = get_object_or_404(ProfessionalCertification, pk=pk, created_by=request.user)

    if request.method == 'POST':
        title = certification.title
        certification.delete()
        messages.success(request, f'Certification "{title}" deleted successfully!')
        return redirect('instructor_dashboard')

    return render(request, 'courses/instructor/delete_certification.html', {'certification': certification})


@login_required
def create_course(request, certification_pk=None):
    """Create a new course"""
    if not request.user.can_create_courses():
        messages.error(request, 'You do not have permission to create courses.')
        return redirect('dashboard')

    certification = None
    if certification_pk:
        certification = get_object_or_404(
            ProfessionalCertification,
            pk=certification_pk,
            created_by=request.user
        )

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        cert_id = request.POST.get('certification')
        order = request.POST.get('order', 0)
        thumbnail = request.FILES.get('thumbnail')

        # Get certification if provided
        cert = None
        if cert_id:
            cert = get_object_or_404(ProfessionalCertification, pk=cert_id, created_by=request.user)

        # Create course
        course = Course.objects.create(
            title=title,
            description=description,
            certification=cert,
            created_by=request.user,
            order=order,
            thumbnail=thumbnail
        )

        messages.success(request, f'Course "{title}" created successfully!')
        return redirect('edit_course', pk=course.pk)

    # Get user's certifications for dropdown
    certifications = ProfessionalCertification.objects.filter(created_by=request.user)

    context = {
        'certification': certification,
        'certifications': certifications,
    }
    return render(request, 'courses/instructor/create_course.html', context)


@login_required
def edit_course(request, pk):
    """Edit an existing course"""
    course = get_object_or_404(Course, pk=pk, created_by=request.user)

    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.order = request.POST.get('order', 0)

        cert_id = request.POST.get('certification')
        if cert_id:
            course.certification = get_object_or_404(
                ProfessionalCertification,
                pk=cert_id,
                created_by=request.user
            )
        else:
            course.certification = None

        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']

        course.save()

        messages.success(request, 'Course updated successfully!')
        return redirect('edit_course', pk=pk)

    # Get modules in this course
    modules = course.modules.all().order_by('order')

    # Get user's certifications for dropdown
    certifications = ProfessionalCertification.objects.filter(created_by=request.user)

    context = {
        'course': course,
        'modules': modules,
        'certifications': certifications,
    }
    return render(request, 'courses/instructor/edit_course.html', context)


@login_required
def delete_course(request, pk):
    """Delete a course"""
    course = get_object_or_404(Course, pk=pk, created_by=request.user)

    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'Course "{title}" deleted successfully!')
        return redirect('instructor_dashboard')

    return render(request, 'courses/instructor/delete_course.html', {'course': course})


@login_required
def create_module(request, course_pk):
    """Create a new module in a course"""
    course = get_object_or_404(Course, pk=course_pk, created_by=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        module_type = request.POST.get('module_type')
        order = request.POST.get('order', 0)
        text_content = request.POST.get('text_content', '')
        video_duration = request.POST.get('video_duration', 0)

        # Create module
        module = Module.objects.create(
            course=course,
            title=title,
            module_type=module_type,
            order=order,
            text_content=text_content,
        )

        # Handle file uploads
        if 'picture' in request.FILES:
            module.picture = request.FILES['picture']

        if 'video' in request.FILES:
            module.video = request.FILES['video']

        module.save()

        messages.success(request, f'Module "{title}" created successfully!')
        return redirect('edit_course', pk=course_pk)

    context = {
        'course': course,
    }
    return render(request, 'courses/instructor/create_module.html', context)


@login_required
def edit_module(request, pk):
    """Edit an existing module"""
    module = get_object_or_404(Module, pk=pk, course__created_by=request.user)

    if request.method == 'POST':
        module.title = request.POST.get('title')
        module.module_type = request.POST.get('module_type')
        module.order = request.POST.get('order', 0)
        module.text_content = request.POST.get('text_content', '')
        module.video_duration = request.POST.get('video_duration', 0)

        if 'picture' in request.FILES:
            module.picture = request.FILES['picture']

        if 'video' in request.FILES:
            module.video = request.FILES['video']

        module.save()

        messages.success(request, 'Module updated successfully!')
        return redirect('edit_course', pk=module.course.pk)

    context = {
        'module': module,
    }
    return render(request, 'courses/instructor/edit_module.html', context)


@login_required
def delete_module(request, pk):
    """Delete a module"""
    module = get_object_or_404(Module, pk=pk, course__created_by=request.user)
    course_pk = module.course.pk

    if request.method == 'POST':
        title = module.title
        module.delete()
        messages.success(request, f'Module "{title}" deleted successfully!')
        return redirect('edit_course', pk=course_pk)

    context = {
        'module': module,
    }
    return render(request, 'courses/instructor/delete_module.html', context)


# =====================================
# ENROLLMENT VIEWS
# =====================================

@login_required
def enroll_certification(request, pk):
    """Enroll in a certification/specialization"""
    certification = get_object_or_404(ProfessionalCertification, pk=pk, is_active=True)

    # Check if already enrolled
    if certification.is_user_enrolled(request.user):
        messages.info(request, 'You are already enrolled in this certification.')
        return redirect('certification_detail', pk=pk)

    # Create enrollment
    CertificationEnrollment.objects.create(
        user=request.user,
        certification=certification
    )

    messages.success(request, f'Successfully enrolled in {certification.title}!')
    return redirect('certification_detail', pk=pk)


@login_required
def unenroll_certification(request, pk):
    """Unenroll from a certification"""
    certification = get_object_or_404(ProfessionalCertification, pk=pk)

    enrollment = CertificationEnrollment.objects.filter(
        user=request.user,
        certification=certification
    ).first()

    if enrollment:
        enrollment.delete()
        messages.success(request, f'Unenrolled from {certification.title}.')
    else:
        messages.info(request, 'You were not enrolled in this certification.')

    return redirect('dashboard')


@login_required
def my_enrollments(request):
    """View all user's enrollments"""
    enrollments = CertificationEnrollment.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('certification')

    enrollment_data = []
    for enrollment in enrollments:
        cert = enrollment.certification
        progress = cert.get_user_progress(request.user)
        is_completed = cert.is_completed_by_user(request.user)

        enrollment_data.append({
            'enrollment': enrollment,
            'certification': cert,
            'progress': progress,
            'is_completed': is_completed,
        })

    context = {
        'enrollment_data': enrollment_data,
    }
    return render(request, 'courses/my_enrollments.html', context)
