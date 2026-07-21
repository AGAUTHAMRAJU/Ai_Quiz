import random
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import EmailOTP


def generate_otp():

    return str(random.randint(100000, 999999))


def create_otp(user):

    EmailOTP.objects.filter(

        user=user,

        is_verified=False

    ).delete()

    otp = generate_otp()

    EmailOTP.objects.create(

        user=user,

        otp=otp

    )

    return otp


def send_otp(user):

    otp = create_otp(user)

    subject = "🔐 AIQuiz Email Verification"

    text_content = f"""
Hello {user.username},

Your One Time Password (OTP) is

{otp}

This OTP is required to verify your email.

If you didn't request this, please ignore this email.

Regards,
AIQuiz Team
"""

    html_content = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

body{{
background:#f5f7fb;
font-family:Arial,sans-serif;
padding:40px;
}}

.card{{
max-width:600px;
margin:auto;
background:white;
border-radius:12px;
overflow:hidden;
box-shadow:0 10px 30px rgba(0,0,0,.08);
}}

.header{{
background:#2563eb;
padding:30px;
text-align:center;
color:white;
}}

.content{{
padding:35px;
}}

.otp{{
margin:30px auto;
width:220px;
background:#eef4ff;
border:2px dashed #2563eb;
text-align:center;
font-size:34px;
font-weight:bold;
letter-spacing:8px;
padding:18px;
border-radius:10px;
color:#2563eb;
}}

.note{{
background:#fff8e6;
padding:15px;
border-left:5px solid orange;
margin-top:25px;
}}

.footer{{
padding:20px;
text-align:center;
font-size:13px;
color:#777;
background:#fafafa;
}}

</style>

</head>

<body>

<div class="card">

<div class="header">

<h1>

AIQuiz

</h1>

<p>

AI Powered Assessment Platform

</p>

</div>

<div class="content">

<h2>

Hello {user.username},

</h2>

<p>

Thank you for registering.

Use this OTP to verify your email.

</p>

<div class="otp">

{otp}

</div>

<div class="note">

Never share this OTP with anyone.

</div>

<p>

If this wasn't you, simply ignore this email.

</p>

</div>

<div class="footer">

AIQuiz

<br>

Powered by Django + Groq AI

</div>

</div>

</body>

</html>
"""

    email = EmailMultiAlternatives(
    subject,
    text_content,
    settings.DEFAULT_FROM_EMAIL,
    [user.email],
    )

    email.attach_alternative(html_content, "text/html")

    print("Before email.send()")

    try:
        email.send(fail_silently=False)
        print("Email sent successfully")
    except Exception as e:
        import traceback
        print("SMTP ERROR:")
        traceback.print_exc()
        raise


def resend_otp(user):

    send_otp(user)


from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from .models import UserAnswer, TheoryAnswer


def generate_result_pdf(quiz):

    buffer = BytesIO()

    doc = SimpleDocTemplate(

        buffer,

        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,

    )

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]

    normal = styles["BodyText"]

    story = []

    ####################################################################
    # TITLE
    ####################################################################

    story.append(

        Paragraph(

            "AIQuiz Assessment Report",

            title,

        )

    )

    story.append(Spacer(1, 20))

    ####################################################################
    # STUDENT DETAILS
    ####################################################################

    details = [

        ["Student", quiz.user.get_full_name() or quiz.user.username],

        ["Email", quiz.user.email],

        ["Topic", quiz.topic],

        ["Difficulty", quiz.difficulty],

        ["Assessment Type", quiz.quiz_type],

        ["Date", quiz.created_at.strftime("%d-%m-%Y %I:%M %p")],

    ]

    table = Table(

        details,

        colWidths=[160, 320]

    )

    table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,colors.grey),

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#0d6efd")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.whitesmoke),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8),

        ])

    )

    story.append(table)

    story.append(Spacer(1,20))

    ####################################################################
    # SCORE
    ####################################################################

    max_marks = quiz.mcq_count + (quiz.theory_count * 10)

    score = [

        ["MCQ Score",f"{quiz.mcq_score}/{quiz.mcq_count}"],

        ["Theory Score",f"{quiz.theory_score}/{quiz.theory_count*10}"],

        ["Total Score",f"{quiz.total_score}/{max_marks}"],

        ["Percentage",f"{quiz.percentage}%"],

    ]

    score_table = Table(

        score,

        colWidths=[170,170]

    )

    score_table.setStyle(

        TableStyle([

            ("GRID",(0,0),(-1,-1),0.5,colors.black),

            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#198754")),

            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.white),

            ("BOTTOMPADDING",(0,0),(-1,-1),8),

            ("TOPPADDING",(0,0),(-1,-1),8),

        ])

    )

    story.append(score_table)

    story.append(Spacer(1,20))

    ####################################################################
    # AI FEEDBACK
    ####################################################################

    if quiz.ai_feedback:

        story.append(

            Paragraph(

                "AI Feedback",

                heading,

            )

        )

        story.append(

            Paragraph(

                quiz.ai_feedback.replace("\n","<br/>"),

                normal,

            )

        )

        story.append(Spacer(1,20))

    ####################################################################
    # MCQ REVIEW
    ####################################################################

    story.append(

        Paragraph(

            "MCQ Review",

            heading,

        )

    )

    story.append(Spacer(1,10))

    answers = UserAnswer.objects.filter(

        quiz=quiz

    ).select_related("question")

    if answers.exists():

        for i, ans in enumerate(answers,1):

            story.append(

                Paragraph(

                    f"<b>Q{i}. {ans.question.question}</b>",

                    normal

                )

            )

            story.append(

                Paragraph(

                    f"<b>Your Answer:</b> {ans.selected_answer or 'Not Answered'}",

                    normal

                )

            )

            story.append(

                Paragraph(

                    f"<b>Correct Answer:</b> {ans.question.correct_answer}",

                    normal

                )

            )

            story.append(

                Paragraph(

                    f"<b>Explanation:</b> {ans.question.explanation}",

                    normal

                )

            )

            story.append(Spacer(1,12))

    ####################################################################
    # THEORY REVIEW
    ####################################################################

    theory = TheoryAnswer.objects.filter(

        quiz=quiz

    ).select_related("question")

    if theory.exists():

        story.append(PageBreak())

        story.append(

            Paragraph(

                "Theory Evaluation",

                heading,

            )

        )

        story.append(Spacer(1,15))

        for i, ans in enumerate(theory,1):

            story.append(

                Paragraph(

                    f"<b>Q{i}. {ans.question.question}</b>",

                    normal,

                )

            )

            story.append(

                Paragraph(

                    f"<b>Your Answer:</b><br/>{ans.answer}",

                    normal,

                )

            )

            story.append(

                Paragraph(

                    f"<b>AI Feedback:</b><br/>{ans.feedback}",

                    normal,

                )

            )

            story.append(

                Paragraph(

                    f"<b>Marks:</b> {ans.score}/10",

                    normal,

                )

            )

            story.append(Spacer(1,15))

    ####################################################################

    story.append(Spacer(1,20))

    story.append(

        Paragraph(

            "<b>Generated by AIQuiz Developed by GM</b>",

            styles["Italic"],

        )

    )

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf













