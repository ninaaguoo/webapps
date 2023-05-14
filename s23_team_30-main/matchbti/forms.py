from django import forms
from matchbti.models import User, Profile, mbti_choices
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
MAX_UPLOAD_SIZE = 2500000


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=200, widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    
phone_regex = RegexValidator(regex=r'^\d{10}$', message='Phone number must be 10 digits.')

class RegisterForm(forms.Form):
    username   = forms.CharField(max_length=20)
    password  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput())
    confirm_password  = forms.CharField(max_length=200,
                                 label='Confirm password',  
                                 widget=forms.PasswordInput())
    # phone_number      = forms.CharField(max_length=12,
    #                              widget = forms.TextInput())
    phone_number = forms.CharField(validators=[phone_regex], max_length=10, widget=forms.TextInput())
    email = forms.CharField(max_length=50,
                            widget = forms.EmailInput())
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('picture', 'user', 'age', 'mbti', 'bio', 'height', 'heightInches', 'gender', 'sexuality', 'preferences', 'ethnicity', 'religion', 'school', 'work')
        exclude = (
            'user',
        )
        widgets = {
            'bio': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': '3'}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture'})
        }
        labels = {
            'bio': "Bio",
            'picture': "Upload image",
            'height': "Height in Feet",
            'heightInches': "Height in Inches"
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if instance:
            self.initial['picture'] = instance.picture
            self.initial['age'] = instance.age
            self.initial['mbti'] = instance.mbti
            self.initial['bio'] = instance.bio
            self.initial['height'] = instance.height
            self.initial['heightInches'] = instance.heightInches
            self.initial['gender'] = instance.gender
            self.initial['sexuality'] = instance.sexuality
            self.initial['preferences'] = instance.preferences
            self.initial['ethnicity'] = instance.ethnicity
            self.initial['religion'] = instance.religion
            self.initial['school'] = instance.school
            self.initial['work'] = instance.work

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture
    
class AgeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('age',)

    def __init__(self, *args, **kwargs):
        super(AgeForm, self).__init__(*args, **kwargs)
        self.fields['age'].widget.attrs['min'] = 1

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 18:
            raise forms.ValidationError("You must be 18+")
        if age > 100:
            raise forms.ValidationError("Please enter a valid age")
        return age
    
class GenderForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('gender',)

class EthnicityForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('ethnicity',)

class HeightForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('height','heightInches')
    
    def __init__(self, *args, **kwargs):
        super(HeightForm, self).__init__(*args, **kwargs)
        self.fields['height'].widget.attrs['min'] = 1
        self.fields['height'].widget.attrs['max'] = 10
        self.fields['heightInches'].widget.attrs['min'] = 0
        self.fields['heightInches'].widget.attrs['max'] = 11

class MBTIForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('mbti',)

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('preferences',)

class SexualityForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('sexuality',)

class ReligionForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('religion',)

class SchoolForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('school',)

class WorkForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('work',)

class NewPicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('picture',)

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class BioForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)

