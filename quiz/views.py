from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import traceback
from .forms import RegisterForm

from .models import (
    Quiz,
    Question,
    TheoryQuestion,
    UserAnswer,
    TheoryAnswer,
    UploadedPDF,
    PreviousQuestion,
)

from .utils import (
    send_otp,
    resend_otp,
)

from .pdf_utils import extract_text_from_pdf

from .groq_service import (
    generate_assessment,
    generate_pdf_mcqs,
    generate_pdf_theory,
    evaluate_theory_answers,
    generate_feedback,
)
from django.db import transaction
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .utils import generate_result_pdf
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import RegisterForm
from .models import EmailOTP
from .utils import send_otp


def home(request):
    return render(request, "home.html")

# def register(request):

#     if request.user.is_authenticated:
#         return redirect("dashboard")

#     form = RegisterForm()

#     if request.method == "POST":

#         form = RegisterForm(request.POST)

#         if form.is_valid():

#             user = User.objects.create_user(

#                 username=form.cleaned_data["username"],

#                 email=form.cleaned_data["email"],

#                 password=form.cleaned_data["password"],

#                 is_active=False,

#             )

#             send_otp(user)

#             request.session["otp_user"] = user.id

#             messages.success(
#                 request,
#                 "OTP has been sent to your email."
#             )

#             return redirect("verify_otp")

#         else:

#             for field in form.errors:

#                 for error in form.errors[field]:

#                     messages.error(request, error)

#     return render(
#         request,
#         "register.html",
#         {
#             "form": form
#         }
#     )

def register(request):

    if request.user.is_authenticated:

        return redirect("dashboard")

    form = RegisterForm()

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            try:

                print("=" * 60)
                print("REGISTER FORM VALID")
                print("Username :", form.cleaned_data["username"])
                print("Email    :", form.cleaned_data["email"])
                print("=" * 60)

                user = User.objects.create_user(

                    username=form.cleaned_data["username"],

                    email=form.cleaned_data["email"],

                    password=form.cleaned_data["password"],

                    is_active=False,

                )

                print("USER CREATED :", user.username)

                send_otp(user)

                print("OTP SENT SUCCESSFULLY")

                request.session["otp_user"] = user.id

                messages.success(

                    request,

                    "OTP has been sent to your email."

                )

                return redirect("verify_otp")

            except Exception as e:

                print("=" * 60)
                print("REGISTER ERROR")
                print(str(e))
                print("=" * 60)

                if "user" in locals():

                    user.delete()

                messages.error(

                    request,

                    "Unable to send OTP. Please try again."

                )

        else:

            print("=" * 60)
            print("FORM ERRORS")
            print(form.errors)
            print("=" * 60)

            for field in form.errors:

                for error in form.errors[field]:

                    messages.error(

                        request,

                        error

                    )

    return render(

        request,

        "register.html",

        {

            "form": form

        }

    )





def verify_otp(request):

    user_id = request.session.get("otp_user")

    if not user_id:

        messages.error(
            request,
            "Registration session expired."
        )

        return redirect("register")

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        messages.error(
            request,
            "User not found."
        )

        return redirect("register")

    if request.method == "POST":

        otp = request.POST.get("otp")

        otp_record = EmailOTP.objects.filter(

            user=user,

            otp=otp,

            is_verified=False

        ).first()

        if otp_record:

            otp_record.is_verified = True

            otp_record.save()

            user.is_active = True

            user.save()

            login(request, user)

            if "otp_user" in request.session:

                del request.session["otp_user"]

            messages.success(

                request,

                "Account verified successfully."

            )

            return redirect("dashboard")

        else:

            messages.error(

                request,

                "Invalid OTP."

            )

    return render(

        request,

        "verify_otp.html"

    )

def resend_otp_view(request):

    user_id = request.session.get("otp_user")

    if not user_id:

        messages.error(

            request,

            "Registration session expired."

        )

        return redirect("register")

    try:

        user = User.objects.get(id=user_id)

    except User.DoesNotExist:

        return redirect("register")

    EmailOTP.objects.filter(

        user=user,

        is_verified=False

    ).delete()

    send_otp(user)

    messages.success(

        request,

        "A new OTP has been sent."

    )

    return redirect("verify_otp")

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        print("=" * 50)
        print("Username:", username)
        print("Password:", password)

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        print("Authenticated User:", user)
        print("=" * 50)

        if user is not None:

            login(request, user)

            print("LOGIN SUCCESS")

            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")

@login_required
def dashboard(request):

    quizzes = Quiz.objects.filter(
        user=request.user
    ).order_by("-created_at")

    total_quizzes = quizzes.count()

    best_score = 0

    average_score = 0

    if quizzes.exists():

        best_score = max(
            quiz.total_score
            for quiz in quizzes
        )

        average_score = round(
            sum(
                quiz.percentage
                for quiz in quizzes
            ) / total_quizzes,
            2
        )

    return render(
        request,
        "dashboard.html",
        {
            "quizzes": quizzes,
            "total_quizzes": total_quizzes,
            "best_score": best_score,
            "average_score": average_score,
        }
    )

@login_required
def profile(request):

    quizzes = Quiz.objects.filter(user=request.user)

    total = quizzes.count()

    mcq = 0

    theory = 0

    average = 0

    if total:

        mcq = sum(i.mcq_score for i in quizzes)

        theory = round(
            sum(i.theory_score for i in quizzes),
            2
        )

        average = round(
            sum(i.percentage for i in quizzes) / total,
            2
        )

    return render(
        request,
        "profile.html",
        {
            "total": total,
            "mcq": mcq,
            "theory": theory,
            "average": average,
        }
    )

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email").strip()

        try:

            user = User.objects.get(email=email)

        except User.DoesNotExist:

            return render(
                request,
                "forgot_password.html",
                {
                    "error": "Email not registered."
                }
            )

        send_otp(user)

        request.session["reset_user"] = user.id

        return redirect("verify_reset_otp")

    return render(request, "forgot_password.html")

def verify_reset_otp(request):

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        otp = request.POST.get("otp")

        record = EmailOTP.objects.filter(
            user=user,
            otp=otp,
            is_verified=False
        ).first()

        if record:

            record.is_verified = True

            record.save()

            request.session["otp_verified"] = True

            return redirect("reset_password")

        return render(
            request,
            "verify_reset_otp.html",
            {
                "error":"Invalid OTP"
            }
        )

    return render(
        request,
        "verify_reset_otp.html"
    )

def reset_password(request):

    if not request.session.get("otp_verified"):
        return redirect("forgot_password")

    user = User.objects.get(
        id=request.session["reset_user"]
    )

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:

            return render(
                request,
                "reset_password.html",
                {
                    "error": "Passwords do not match."
                }
            )

        user.password = make_password(password)

        user.save()

        request.session.flush()

        return redirect("login")

    return render(request, "reset_password.html")

@login_required
def take_quiz(request, quiz_id):

    quiz = get_object_or_404(

        Quiz,

        id=quiz_id,

        user=request.user

    )

    if UserAnswer.objects.filter(

        quiz=quiz

    ).exists():

        return redirect(

            "result",

            quiz.id

        )

    mcq_questions = Question.objects.filter(

        quiz=quiz

    )

    theory_questions = TheoryQuestion.objects.filter(

        quiz=quiz

    )

    context = {

        "quiz": quiz,

        "mcq_questions": mcq_questions,

        "theory_questions": theory_questions,

        "mcq_total": mcq_questions.count(),

        "theory_total": theory_questions.count(),

        "total_questions": quiz.total_questions,

    }

    return render(

        request,

        "take_quiz.html",

        context

    )

@login_required
def result(request, quiz_id):

    quiz = get_object_or_404(
        Quiz,
        id=quiz_id,
        user=request.user
    )

    mcq_answers = list(
        UserAnswer.objects.filter(
            quiz=quiz
        ).select_related("question")
    )

    theory_answers = list(
        TheoryAnswer.objects.filter(
            quiz=quiz
        ).select_related("question")
    )

    print("\n" + "=" * 80)
    print("MCQ ANSWERS SENT TO TEMPLATE")
    print("=" * 80)

    for a in mcq_answers:
        print({
            "question": a.question.question,
            "selected": a.selected_answer,
            "correct": a.question.correct_answer,
            "explanation": a.question.explanation,
            "is_correct": a.is_correct,
        })

    print("\n" + "=" * 80)
    print("THEORY ANSWERS SENT TO TEMPLATE")
    print("=" * 80)

    for a in theory_answers:
        print({
            "question": a.question.question,
            "answer": a.answer,
            "feedback": a.feedback,
            "score": a.score,
        })

    context = {
        "quiz": quiz,
        "mcq_answers": mcq_answers,
        "theory_answers": theory_answers,
        "feedback": quiz.ai_feedback,
        "mcq_total": quiz.mcq_count,
        "theory_total": quiz.theory_count,
        "max_marks": quiz.max_marks(),
    }

    return render(
        request,
        "result.html",
        context
    )

@login_required
def history(request):

    quizzes = Quiz.objects.filter(

        user=request.user

    ).order_by(

        "-created_at"

    )

    return render(

        request,

        "history.html",

        {

            "quizzes": quizzes

        }

    )

@login_required
def export_result_pdf(request, quiz_id):

    quiz = get_object_or_404(

        Quiz,

        id=quiz_id,

        user=request.user

    )

    mcq_answers = UserAnswer.objects.filter(

        quiz=quiz

    ).select_related(

        "question"

    )

    theory_answers = TheoryAnswer.objects.filter(

        quiz=quiz

    ).select_related(

        "question"

    )

    pdf = generate_result_pdf(quiz)

    response = HttpResponse(

        pdf,

        content_type="application/pdf"

    )

    response["Content-Disposition"] = (

        f'attachment; filename="{quiz.topic}_Result.pdf"'

    )

    return response

@login_required
def submit_quiz(request, quiz_id):

    if request.method != "POST":

        return redirect("dashboard")

    quiz = get_object_or_404(

        Quiz,

        id=quiz_id,

        user=request.user

    )

    if UserAnswer.objects.filter(quiz=quiz).exists():

        return redirect(

            "result",

            quiz.id

        )

    mcq_questions = Question.objects.filter(

        quiz=quiz

    )

    theory_questions = TheoryQuestion.objects.filter(

        quiz=quiz

    )

    ####################################################
    # SAVE MCQS
    ####################################################

    mcq_score = 0

    for question in mcq_questions:

        selected = request.POST.get(

            f"mcq_{question.id}",

            ""

        )

        correct = selected == question.correct_answer

        if correct:

            mcq_score += 1

        UserAnswer.objects.create(

            quiz=quiz,

            question=question,

            selected_answer=selected,

            is_correct=correct

        )

    ####################################################
    # SAVE THEORY
    ####################################################

    theory_score = 0

    if theory_questions.exists():

        theory_payload = []

        student_answers = []

        theory_list = list(theory_questions)

        for question in theory_list:

            answer = request.POST.get(

                f"theory_{question.id}",

                ""

            )

            theory_payload.append(

                {

                    "question": question.question,

                    "expected_answer": question.expected_answer

                }

            )

            student_answers.append(answer)

        print("\n" + "=" * 80)
        print("THEORY PAYLOAD")
        print(theory_payload)
        print("=" * 80)

        print("\n" + "=" * 80)
        print("STUDENT ANSWERS")
        print(student_answers)
        print("=" * 80)

        try:

            evaluation = evaluate_theory_answers(

                theory_payload,

                student_answers

            )

            print("\n" + "=" * 80)
            print("EVALUATION RETURNED FROM GROQ")
            print(evaluation)
            print(type(evaluation))
            print("=" * 80)

        except Exception:

            traceback.print_exc()

            messages.error(

                request,

                "Theory evaluation failed."

            )

            return redirect(

                "take_quiz",

                quiz.id

            )

        for question, student_answer, result in zip(

            theory_list,

            student_answers,

            evaluation

        ):

            print()

            print("CREATING THEORY ANSWER")

            print(question.question)

            print(student_answer)

            print(result)

            score = float(

                result.get(

                    "score",

                    0

                )

            )

            theory_score += score

            TheoryAnswer.objects.create(

                quiz=quiz,

                question=question,

                answer=student_answer,

                score=score,

                feedback=result.get(

                    "feedback",

                    ""

                )

            )

    ####################################################
    # SCORE
    ####################################################

    quiz.mcq_score = mcq_score

    quiz.theory_score = theory_score

    quiz.total_score = mcq_score + theory_score

    max_marks = quiz.max_marks()

    if max_marks:

        quiz.percentage = round(

            (quiz.total_score / max_marks) * 100,

            2

        )

    else:

        quiz.percentage = 0

    quiz.ai_feedback = generate_feedback(

        quiz.topic,

        quiz.total_score,

        max_marks

    )

    quiz.save()

    ####################################################
    # EMAIL
    ####################################################

    try:

        pdf = generate_result_pdf(quiz)

        html = render_to_string(

            "emails/result_email.html",

            {

                "quiz": quiz,

                "user": request.user

            }

        )

        email = EmailMessage(

            subject=f"Assessment Result - {quiz.topic}",

            body=html,

            from_email=settings.DEFAULT_FROM_EMAIL,

            to=[request.user.email]

        )

        email.content_subtype = "html"

        email.attach(

            f"{quiz.topic}.pdf",

            pdf,

            "application/pdf"

        )

        email.send(

            fail_silently=True

        )

    except Exception:

        traceback.print_exc()

    return redirect(

        "result",

        quiz.id

    )

@login_required
def generate_quiz(request):
    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        difficulty = request.POST.get("difficulty")

        # Safely convert post parameters to integers
        try:
            mcqs = int(request.POST.get("mcqs", 0))
            theory = int(request.POST.get("theory", 0))
        except (ValueError, TypeError):
            messages.error(request, "Invalid numbers provided for questions.")
            return redirect("generate_quiz")

        assessment_type = request.POST.get("assessment_type")
        uploaded_pdf = request.FILES.get("pdf")
        pdf_obj = None

        try:
            # ==========================================
            # 1. GENERATION LAYER (PDF vs Topic)
            # ==========================================
            if assessment_type == "PDF":
                if not uploaded_pdf:
                    messages.error(request, "Please upload a PDF.")
                    return redirect("generate_quiz")

                if not uploaded_pdf.name.lower().endswith(".pdf"):
                    messages.error(request, "Only PDF files are allowed.")
                    return redirect("generate_quiz")

                if uploaded_pdf.size > 10 * 1024 * 1024:
                    messages.error(request, "Maximum PDF size is 10MB.")
                    return redirect("generate_quiz")

                # Create file tracking object
                pdf_obj = UploadedPDF.objects.create(
                    user=request.user, file=uploaded_pdf
                )
                pdf_text = extract_text_from_pdf(pdf_obj.file.path)

                # Fetch history tracking to avoid repeats
                previous_mcqs = list(
                    PreviousQuestion.objects.filter(
                        pdf=pdf_obj, question_type="MCQ"
                    ).values_list("question", flat=True)
                )
                previous_theory = list(
                    PreviousQuestion.objects.filter(
                        pdf=pdf_obj, question_type="THEORY"
                    ).values_list("question", flat=True)
                )

                print("\n========== GENERATING PDF MCQS ==========\n")
                mcq_data = generate_pdf_mcqs(
                    pdf_text, mcqs, previous_mcqs
                )

                print("\n========== GENERATING PDF THEORY ==========\n")
                theory_data = generate_pdf_theory(
                    pdf_text, theory, previous_theory
                )

                assessment = {
                    "mcqs": mcq_data.get("mcqs", []),
                    "theory": theory_data.get("theory", []),
                }
                topic = uploaded_pdf.name
                quiz_type = "PDF"

            else:
                if topic == "":
                    messages.error(request, "Topic cannot be empty.")
                    return redirect("generate_quiz")

                assessment = generate_assessment(
                    topic, difficulty, mcqs, theory
                )
                quiz_type = "TOPIC"

            # ==========================================
            # 2. DATABASE PERSISTENCE LAYER (Atomic)
            # ==========================================
            with transaction.atomic():
                # Step A: Main Quiz Object
                quiz = Quiz.objects.create(
                    user=request.user,
                    quiz_type=quiz_type,
                    pdf=pdf_obj,
                    topic=topic,
                    difficulty=difficulty,
                    total_questions=mcqs + theory,
                    mcq_count=mcqs,
                    theory_count=theory,
                )

                # Step B: Process & Save Multiple Choice Questions
                print("\n========== SAVING MCQS ==========\n")
                for q in assessment.get("mcqs", []):
                    question_text = q.get("question", "").strip()
                    options = q.get("options", ["", "", "", ""])

                    # Enforce option spacing safety
                    while len(options) < 4:
                        options.append("")

                    # Map numerical answer string indicators back to target text values
                    answer = str(q.get("answer", "")).strip()
                    if answer == "1":
                        answer = options[0]
                    elif answer == "2":
                        answer = options[1]
                    elif answer == "3":
                        answer = options[2]
                    elif answer == "4":
                        answer = options[3]

                    Question.objects.create(
                        quiz=quiz,
                        question=question_text,
                        option1=options[0],
                        option2=options[1],
                        option3=options[2],
                        option4=options[3],
                        correct_answer=answer,
                        explanation=q.get(
                            "explanation", "Explanation not provided."
                        ),
                    )

                    if pdf_obj:
                        PreviousQuestion.objects.get_or_create(
                            pdf=pdf_obj,
                            question=question_text,
                            question_type="MCQ",
                        )

                # Step C: Process & Save Open-Ended Theory Questions
                print("\n========== SAVING THEORY ==========\n")
                for q in assessment.get("theory", []):
                    question_text = q.get("question", "").strip()
                    # Handled both common key mappings ('answer' / 'expected_answer') safely
                    expected_answer = q.get("expected_answer", q.get("answer", "")).strip()

                    TheoryQuestion.objects.create(
                        quiz=quiz,
                        question=question_text,
                        expected_answer=expected_answer,
                    )

                    if pdf_obj:
                        PreviousQuestion.objects.get_or_create(
                            pdf=pdf_obj,
                            question=question_text,
                            question_type="THEORY",
                        )

            # Success response out of block scope boundaries
            messages.success(request, "Assessment generated successfully.")
            return redirect("take_quiz", quiz_id=quiz.id)

        except Exception as e:
            traceback.print_exc()
            messages.error(request, f"Error generating assessment: {str(e)}")
            return redirect("generate_quiz")

    # Render template layer on safe GET requests
    return render(request, "generate_quiz.html")















