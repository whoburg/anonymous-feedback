from django.contrib import admin

from .models import Survey, Question


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['survey_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [QuestionInline]

admin.site.register(Survey, SurveyAdmin)
