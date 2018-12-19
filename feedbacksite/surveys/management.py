from .models import Assignment

def create_symmetric_assignments(group, survey):
    for user in group.user_set.all():
        create_assignments_user_reviews_group(group, survey, user)

def create_assignments_user_reviews_group(group, survey, user):
    for r in group.user_set.all():
        if r == user:
            continue
        Assignment.objects.get_or_create(survey=survey, user=user, recipient=r)

def create_assignments_group_reviews_recipient(group, survey, recipient):
    for user in group.user_set.all():
        if user == recipient:
            continue
        Assignment.objects.get_or_create(survey=survey, user=user, recipient=r)
