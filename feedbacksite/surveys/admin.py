from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Survey, Question, Feedback, Assignment


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 1


class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['title', 'results_published']}),
        ('Date information', {'fields': ['pub_date', 'due_date']}),
    ]
    inlines = [QuestionInline, AssignmentInline]

UserAdmin.list_display += ('publickey',)
UserAdmin.list_filter += ('publickey',)

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Feedback)
