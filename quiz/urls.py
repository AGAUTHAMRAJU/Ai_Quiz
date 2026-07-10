from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("generate-quiz/", views.generate_quiz, name="generate_quiz"),
    path("take-quiz/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("submit-quiz/<int:quiz_id>/", views.submit_quiz, name="submit_quiz"),
    path("result/<int:quiz_id>/", views.result, name="result"),
    path("history/", views.history, name="history"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("profile/", views.profile, name="profile"),
    path(
    "resend-otp/",
    views.resend_otp_view,
    name="resend_otp"
),
path("forgot-password/", views.forgot_password, name="forgot_password"),
path("forgot-password/verify/", views.verify_reset_otp, name="verify_reset_otp"),
path("reset-password/", views.reset_password, name="reset_password"),
path(
    "result/<int:quiz_id>/pdf/",
    views.export_result_pdf,
    name="export_result_pdf",
),



]