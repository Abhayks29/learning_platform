from django.db import models
from apps.users.models import User
from apps.courses.models import Course


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_submission_count(self):
        return self.submissions.count()

    def get_pending_count(self):
        return self.submissions.filter(status=Submission.PENDING).count()


class Submission(models.Model):
    PENDING = 'pending'
    GRADED = 'graded'
    STATUS_CHOICES = [(PENDING, 'Pending'), (GRADED, 'Graded')]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    text_response = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({self.status})"

    def get_grade_percent(self):
        if self.score is None or self.assignment.max_score == 0:
            return None
        return round((self.score / self.assignment.max_score) * 100, 1)
