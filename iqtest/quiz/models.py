from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
    
# The Question model will store the text of the question, the type of question (multiple choice or image based),

class Question(models.Model):
    source_id = models.CharField(max_length=50, unique=True)
    text = models.TextField()  # The textual part of the question
    options = models.JSONField()  # Store options as JSON

    #TODO

    correct_answer = models.CharField(max_length=255)  # The key of the correct option
    hint = models.TextField(max_length=255, blank=True, default="") # Hint for the question
    category = models.CharField(max_length=50)  # e.g., "logic-dynamics", "verbal"
    image = models.ImageField(upload_to='questions/images/', null=True, blank=True)  # Optional image
    has_image = models.BooleanField(default=False)  # Flag to indicate if the question has an image

    def __str__(self):
        return f"{self.category} - {self.text[:50]}"
    
    class Meta:
        ordering = ['id']


class OptionImage(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='option_images')
    key = models.CharField(max_length=10)  # e.g., "0", "1", "2", "3"
    image = models.ImageField(upload_to='option_images/')

    def __str__(self):
        return f"Option {self.key} for Question {self.question.id}"

class TestSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.ManyToManyField('Question', related_name='test_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('shared', 'Shared'), ('failed', 'Failed')],
        default='pending'
    )

    def __str__(self):
        return f"{self.user.username} - Test Session {self.id}"
    
    def get_stripe_url(self):
        if not self.stripe_session_id:
            # no payment initiated
            return None
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # stripe path for test payment
            path = '/test/'
        else:
            # path for live payment
            path = '/'
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_session_id}"

class UserAnswer(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255, null=True, blank=True)  # e.g., "0" for option key
    is_correct = models.BooleanField(null=True, blank=True)
    hint = models.TextField(max_length=255, blank=True, default="")  # Added hint field to store the hint of the question

    def __str__(self):
        return f"{self.test_session.user.username} - Q{self.question.id}"
    

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_session = models.ForeignKey('TestSession', on_delete=models.CASCADE)  # Link to your test session model
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # New field to track approval status

    def __str__(self):
        return f"Review by {self.user.username} for session {self.test_session.id}"