from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .image_utils import process_profile_picture

# -------------------------------
# Custom User Model
# -------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Administrator'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/',
                                        blank=True, 
                                        null=True,
                                        help_text="Upload a profile picture (will be cropped to square)")

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

def save(self, *args, **kwargs):
        """Override save to process profile picture"""
        # Check if profile_picture was uploaded/changed
        if self.profile_picture and hasattr(self.profile_picture, 'file'):
            try:
                self.profile_picture = process_profile_picture(self.profile_picture)
            except Exception as e:
                print(f"Could not process profile picture: {e}")
        
        super().save(*args, **kwargs)




# -------------------------------
# Course Model
# -------------------------------
class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return f"{self.code} - {self.name}"


# -------------------------------
# Feedback Model
# -------------------------------
class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="student_feedback")
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lecturer_feedback")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.FloatField()
    teaching_rating = models.FloatField(blank=True, null=True)
    communication_rating = models.FloatField(blank=True, null=True)
    engagement_rating = models.FloatField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback by {self.student.username} for {self.lecturer.username}"


# -------------------------------
# AI Suggestion Model
# -------------------------------
class Suggestion(models.Model):
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_suggestions")
    suggestions_text = models.TextField()
    based_on_feedback_count = models.PositiveIntegerField(default=0)
    generated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Suggestion for {self.lecturer.username} on {self.generated_at.strftime('%Y-%m-%d')}"

