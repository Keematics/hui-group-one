from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone


class User(AbstractUser):
    """Extended User model with additional fields and role management"""

    # User roles
    ROLE_LEARNER = 'learner'
    ROLE_INSTRUCTOR = 'instructor'

    ROLE_CHOICES = [
        (ROLE_LEARNER, 'Learner'),
        (ROLE_INSTRUCTOR, 'Instructor'),
    ]

    matric_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    profile_picture = CloudinaryField('profile_picture', null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Brief biography or description")
    date_joined = models.DateTimeField(default=timezone.now)

    # Role field - Group members are instructors by default, others are learners
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_LEARNER,
        help_text="User role: Instructor can create courses, Learner can only take courses"
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def is_instructor(self):
        """Check if user has instructor privileges"""
        return self.role == self.ROLE_INSTRUCTOR or self.is_staff

    def can_create_courses(self):
        """Check if user can create and manage courses"""
        return self.is_instructor() or self.is_superuser


class GroupMember(models.Model):
    """Group members for display on homepage"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='group_profile')
    matric_number = models.CharField(max_length=20)
    title = models.CharField(max_length=100, help_text="e.g., Group Leader, Developer, Designer")
    is_leader = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order on homepage")

    class Meta:
        ordering = ['order', '-is_leader']
        db_table = 'group_members'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class ProfessionalCertification(models.Model):
    """Professional Certification or Specialization that contains multiple courses"""

    # Certification types
    TYPE_PROFESSIONAL = 'professional'
    TYPE_SPECIALIZATION = 'specialization'

    TYPE_CHOICES = [
        (TYPE_PROFESSIONAL, 'Professional Certificate'),
        (TYPE_SPECIALIZATION, 'Specialization'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    certification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PROFESSIONAL,
        help_text="Type of certification"
    )
    thumbnail = CloudinaryField('certification_thumbnail', null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_certifications',
        help_text="Instructor who created this certification"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'professional_certifications'

    def __str__(self):
        return f"{self.title} ({self.get_certification_type_display()})"

    def get_total_courses(self):
        return self.courses.count()

    def get_user_progress(self, user):
        """Calculate user's progress across all courses in this certification (only if enrolled)"""
        # Check if user is enrolled in this certification
        if not self.enrollments.filter(user=user).exists():
            return 0

        total_courses = self.courses.filter(is_active=True).count()
        if total_courses == 0:
            return 0

        completed_courses = sum(
            1 for course in self.courses.filter(is_active=True)
            if course.is_completed_by_user(user)
        )

        return (completed_courses / total_courses) * 100

    def is_completed_by_user(self, user):
        """Check if user has completed all courses in this certification (only if enrolled)"""
        # Must be enrolled to get certification certificate
        if not self.enrollments.filter(user=user).exists():
            return False

        active_courses = self.courses.filter(is_active=True)
        if not active_courses.exists():
            return False

        return all(course.is_completed_by_user(user) for course in active_courses)

    def is_user_enrolled(self, user):
        """Check if user is enrolled in this certification"""
        return self.enrollments.filter(user=user).exists()


class Course(models.Model):
    """Course under a Professional Certification (can also be taken independently)"""
    certification = models.ForeignKey(
        ProfessionalCertification,
        on_delete=models.CASCADE,
        related_name='courses',
        null=True,
        blank=True,
        help_text="Parent certification (optional - can be standalone course)"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = CloudinaryField('course_thumbnail', null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_courses',
        help_text="Instructor who created this course"
    )
    order = models.IntegerField(default=0, help_text="Display order within certification")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        db_table = 'courses'

    def __str__(self):
        return f"{self.certification.title} - {self.title}"

    def get_total_modules(self):
        return self.modules.filter(is_active=True).count()

    def get_user_progress(self, user):
        """Calculate user's progress percentage for this course"""
        total_modules = self.modules.filter(is_active=True).count()
        if total_modules == 0:
            return 0

        completed_modules = ModuleProgress.objects.filter(
            user=user,
            module__course=self,
            module__is_active=True,
            is_completed=True
        ).count()

        return (completed_modules / total_modules) * 100

    def is_completed_by_user(self, user):
        """Check if user has completed at least 90% of the modules"""
        progress = self.get_user_progress(user)
        return progress >= 90


class Module(models.Model):
    """Module within a course - can be text, picture, video, or text+picture"""

    MODULE_TYPES = [
        ('text', 'Text Only'),
        ('picture', 'Picture Only'),
        ('video', 'Video'),
        ('text_picture', 'Text and Picture'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    order = models.IntegerField(default=0, help_text="Display order within course")

    # Content fields
    text_content = models.TextField(blank=True, help_text="Rich text content")
    picture = CloudinaryField('module_picture', null=True, blank=True)
    video = CloudinaryField('module_video', resource_type='video', null=True, blank=True)
    video_duration = models.IntegerField(
        default=0,
        help_text="Video duration in seconds (for progress tracking)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        db_table = 'modules'

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_completion_threshold(self):
        """Get the completion threshold for video modules (85%)"""
        if self.module_type == 'video':
            return 0.85
        return 1.0  # 100% for non-video modules

    def is_completed_by_user(self, user):
        """Check if this module is completed by the user"""
        try:
            progress = ModuleProgress.objects.get(user=user, module=self)
            return progress.is_completed
        except ModuleProgress.DoesNotExist:
            return False


class ModuleProgress(models.Model):
    """Track user progress for each module"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress')

    # Progress tracking
    is_completed = models.BooleanField(default=False)
    video_watch_time = models.IntegerField(
        default=0,
        help_text="Seconds watched for video modules"
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'module']
        db_table = 'module_progress'
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {'Completed' if self.is_completed else 'In Progress'}"

    def mark_as_completed(self):
        """Mark module as completed"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()

    def update_video_progress(self, watch_time):
        """Update video watch time and check if completion threshold is met"""
        self.video_watch_time = watch_time

        # Check if user has watched at least 85% of the video
        if self.module.module_type == 'video' and self.module.video_duration > 0:
            threshold = self.module.get_completion_threshold()
            if watch_time >= (self.module.video_duration * threshold):
                self.mark_as_completed()

        self.save()

    def get_progress_percentage(self):
        """Get progress percentage for this module"""
        if self.is_completed:
            return 100

        if self.module.module_type == 'video' and self.module.video_duration > 0:
            return min(100, (self.video_watch_time / self.module.video_duration) * 100)

        return 0


class CourseCertificate(models.Model):
    """Certificate issued when a user completes a course"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_file = CloudinaryField('certificate', null=True, blank=True)

    class Meta:
        unique_together = ['user', 'course']
        db_table = 'course_certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificate - {self.user.get_full_name()} - {self.course.title}"


class ProfessionalCertificationCertificate(models.Model):
    """Certificate issued when a user completes all courses in a professional certification"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='professional_certificates'
    )
    certification = models.ForeignKey(
        ProfessionalCertification,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_file = CloudinaryField('certificate', null=True, blank=True)

    class Meta:
        unique_together = ['user', 'certification']
        db_table = 'professional_certification_certificates'
        ordering = ['-issued_at']

    def __str__(self):
        return f"Professional Certificate - {self.user.get_full_name()} - {self.certification.title}"


class CertificationEnrollment(models.Model):
    """Track which users are enrolled in which certifications/specializations"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certification_enrollments'
    )
    certification = models.ForeignKey(
        ProfessionalCertification,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'certification']
        db_table = 'certification_enrollments'
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.get_full_name()} enrolled in {self.certification.title}"
