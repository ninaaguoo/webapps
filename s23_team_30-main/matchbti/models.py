from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# pip install django-multiselectfield
from multiselectfield import MultiSelectField

#added assertive/turbulent -a, -t
mbti_choices = (('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
                ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
                ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
                ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')) 
                   

gender_choices = (('Woman', 'Woman'), ('Man', 'Man'), ('Nonbinary', 'Nonbinary'))

preference_choices = (('Women', 'Women'), ('Men', 'Men'), ('Nonbinary', 'Nonbinary'), ('Everyone', 'Everyone'))


#add more ethnicities
ethnicity_choices = (('American Indian', 'American Indian',), ('Asian', 'Asian'),
                     ('Black/african descent', 'Black/African Descent'), ('Hispanic/Latino', 'Hispanic/Latino'),
                     ('Middle Eastern', 'Middle Eastern'), ('Pacific Islander', 'Pacific Islander'),
                     ('White/Caucasian', 'White/Caucasian'), ('Other', 'Other'))

religion_choices = (('Agnostic', 'Agnostic'), ('Atheist', 'Atheist'), ('Buddhist', 'Buddhist'),
                    ('Catholic', 'Catholic'), ('Christian', 'Christian'), ('Hindu', 'Hindu'),
                    ('Jewish', 'Jewish'), ('Muslim', 'Muslim'), ('Sikh', 'Sikh'),
                    ('Spiritual', 'Spiritual'), ('Other', 'Other'))

sexuality_choices = (('Straight', 'Straight'), ('Gay', 'Gay'), ('Lesbian', 'Lesbian'),
                     ('Bisexual', 'Bisexual'), ('Asexual', 'Asexual'), ('Demisexual', 'Demisexual'),
                     ('Pansexual', 'Pansexual'), ('Other', 'Other'))

# Create your models here.

class Message(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user")
    receiver = models.ForeignKey(User, on_delete=models.PROTECT, related_name="receiver")
    creation_time = models.DateTimeField(default=now, blank=True)
    
class Profile(models.Model):
    last_name     = models.CharField(max_length=20)
    first_name    = models.CharField(max_length=20)
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=False)
    content_type = models.CharField(max_length=50, default="image/png")
    age = models.IntegerField(blank=False, null=True)
    height = models.IntegerField(blank=False, null=True)
    heightInches = models.IntegerField(blank=False, null=True)
    ethnicity = models.CharField(max_length=50, choices=ethnicity_choices, blank=False, null=True)
    gender = models.CharField(max_length=50, choices=gender_choices, blank=False, null=True)
    sexuality = models.CharField(max_length=50, choices=sexuality_choices, blank=False, null=True)
    preferences = MultiSelectField(max_length=50, choices=preference_choices, blank=False, null=True)
    mbti = models.CharField(max_length=4, choices=mbti_choices, blank=False, null=True)
    religion = models.CharField(max_length=50, choices=religion_choices, blank=False, null=True)
    school = models.CharField(max_length=50, blank=False)
    work = models.CharField(max_length=50, blank=False)
    discoverable = models.ManyToManyField(User, related_name="discoverable", blank=True) # ppl u have not swiped on yet
    likes = models.ManyToManyField(User, related_name="likes", blank=True) # all ppl u liked
    dislikes = models.ManyToManyField(User, related_name="dislikes", blank=True) # all ppl u disliked
    matches = models.ManyToManyField(User, related_name="matches", blank=True) #show up in chatboxes
    messages = models.ManyToManyField(Message, blank=True)
    latitude = models.CharField(max_length=200, blank=False)
    longitude = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return f"Entry(id={self.id})"
    




