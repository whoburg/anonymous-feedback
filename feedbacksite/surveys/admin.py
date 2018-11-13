from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Survey, Question, Feedback


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['survey_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [QuestionInline]

UserAdmin.list_display += ('publickey',)
UserAdmin.list_filter += ('publickey',)

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Feedback)
