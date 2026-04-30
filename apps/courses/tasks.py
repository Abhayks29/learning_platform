from celery import shared_task


@shared_task
def process_video_upload(lesson_id):
    """Generate thumbnail and validate video encoding after upload."""
    from apps.courses.models import Lesson
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        # ffmpeg processing would go here in production
        _ = lesson
    except Lesson.DoesNotExist:
        pass


@shared_task
def send_enrollment_email(user_id, course_id):
    """Send welcome email when student enrolls in a course."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings
    from apps.courses.models import Course

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        send_mail(
            subject=f'Welcome to {course.title}!',
            message=(
                f'Hi {user.first_name or user.username},\n\n'
                f'You have successfully enrolled in "{course.title}".\n\n'
                f'Start learning now at your dashboard.\n\nThe EdTech Team'
            ),
            from_email=settings.EMAIL_HOST_USER or 'noreply@edtech.com',
            recipient_list=[user.email],
            fail_silently=True,
        )
    except (User.DoesNotExist, Course.DoesNotExist):
        pass


@shared_task
def update_course_completion(enrollment_id):
    """Recalculate and update enrollment completion status."""
    from apps.courses.models import Enrollment, LessonProgress
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        total = enrollment.course.lessons.count()
        if total == 0:
            return
        completed = LessonProgress.objects.filter(
            student=enrollment.student,
            lesson__course=enrollment.course,
            completed=True,
        ).count()
        enrollment.completed = (completed == total)
        enrollment.save(update_fields=['completed'])
    except Enrollment.DoesNotExist:
        pass
