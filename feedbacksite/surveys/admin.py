from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Survey, Question, Feedback, PublicKey


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


class PublicKeyInline(admin.StackedInline):
    model = PublicKey
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (PublicKeyInline,)


class SurveyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['survey_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [QuestionInline]

admin.site.register(Survey, SurveyAdmin)
admin.site.register(Feedback)
# Re-register UserAdmin for PublicKey inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
