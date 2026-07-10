from django.db import models
from django.contrib.auth.models import User


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class UploadedPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class PreviousQuestion(models.Model):

    QUESTION_TYPES = (

        ("MCQ", "MCQ"),

        ("THEORY", "THEORY"),

    )

    pdf = models.ForeignKey(

        UploadedPDF,

        on_delete=models.CASCADE,

        related_name="generated_questions"

    )

    question = models.TextField()

    question_type = models.CharField(

        max_length=20,

        choices=QUESTION_TYPES

    )

    created_at = models.DateTimeField(

        auto_now_add=True

    )

    class Meta:

        unique_together = (

            "pdf",

            "question"

        )

    def __str__(self):

        return self.question



class Quiz(models.Model):

    DIFFICULTY = (
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    )

    QUIZ_TYPE = (
        ("TOPIC", "TOPIC"),
        ("PDF", "PDF"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    quiz_type = models.CharField(
        max_length=20,
        choices=QUIZ_TYPE,
        default="TOPIC"
    )

    pdf = models.ForeignKey(
        UploadedPDF,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    topic = models.CharField(
        max_length=200
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY
    )

    mcq_count = models.IntegerField(default=0)

    theory_count = models.IntegerField(default=0)

    total_questions = models.IntegerField(default=0)

    mcq_score = models.IntegerField(default=0)

    theory_score = models.FloatField(default=0)

    total_score = models.FloatField(default=0)

    percentage = models.FloatField(default=0)

    ai_feedback = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-created_at"]

    def max_marks(self):

        return self.mcq_count + (self.theory_count * 10)

    def __str__(self):

        return f"{self.topic} ({self.user.username})"
    
    
class Question(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    option1 = models.CharField(max_length=500)

    option2 = models.CharField(max_length=500)

    option3 = models.CharField(max_length=500)

    option4 = models.CharField(max_length=500)

    correct_answer = models.CharField(max_length=500)

    explanation = models.TextField()

    def __str__(self):
        return self.question


class TheoryQuestion(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    expected_answer = models.TextField()

    def __str__(self):
        return self.question


class UserAnswer(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    selected_answer = models.CharField(
        max_length=500
    )

    is_correct = models.BooleanField(default=False)


class TheoryAnswer(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        TheoryQuestion,
        on_delete=models.CASCADE
    )

    answer = models.TextField()

    score = models.FloatField(default=0)

    feedback = models.TextField(blank=True)