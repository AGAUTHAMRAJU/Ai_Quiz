from django.contrib import admin

from .models import *

admin.site.register(EmailOTP)
admin.site.register(UploadedPDF)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(TheoryQuestion)
admin.site.register(UserAnswer)
admin.site.register(TheoryAnswer)