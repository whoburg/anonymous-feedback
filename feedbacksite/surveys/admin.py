from django.contrib import admin

from .models import Survey, Question, Feedback, PublicKey


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
admin.site.register(Feedback)
admin.site.register(PublicKey)
