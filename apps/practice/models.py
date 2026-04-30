from django.db import models
from django.utils.text import slugify
from apps.users.models import User
from apps.courses.models import Course


class PracticeProblem(models.Model):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    DIFFICULTY_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='problems'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default=EASY)
    tags = models.CharField(max_length=300, blank=True)
    starter_code = models.TextField(blank=True)
    solution_code = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['difficulty', 'title']

    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_acceptance_rate(self):
        total = self.submissions.count()
        if total == 0:
            return 0
        accepted = self.submissions.filter(status=CodeSubmission.ACCEPTED).count()
        return round((accepted / total) * 100, 1)

    def get_difficulty_color(self):
        colors = {self.EASY: 'green', self.MEDIUM: 'yellow', self.HARD: 'red'}
        return colors.get(self.difficulty, 'gray')


class TestCase(models.Model):
    problem = models.ForeignKey(PracticeProblem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        visibility = 'hidden' if self.is_hidden else 'visible'
        return f"TestCase for {self.problem.title} ({visibility})"


class CodeSubmission(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    WRONG = 'wrong'
    ERROR = 'error'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (WRONG, 'Wrong Answer'),
        (ERROR, 'Runtime Error'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_submissions')
    problem = models.ForeignKey(PracticeProblem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=20, default='python')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    output = models.TextField(blank=True)
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.problem.title} ({self.status})"
