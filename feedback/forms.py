from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Course, Feedback


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
        help_text='Optional: Upload a profile picture (will be auto-cropped to square)'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role',
                  'department', 'profile_picture', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 
                                               'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.department = self.cleaned_data.get('department', '')
        if commit:
            user.save()
        return user


class CourseForm(forms.ModelForm):
    """Form for lecturers to add courses"""
    class Meta:
        model = Course
        fields = ['code', 'name', 'department', 'description']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., RCS101'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Information Technology'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computing Science'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional course description'
            }),
        }


class FeedbackForm(forms.ModelForm):
    """Form for students to submit feedback"""
    RATING_CHOICES = [
        ('', 'Select Rating'),
        (5, '5 - Excellent'),
        (4, '4 - Good'),
        (3, '3 - Average'),
        (2, '2 - Below Average'),
        (1, '1 - Poor'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES[1:],  # Exclude empty option
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    teaching_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    communication_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    engagement_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Feedback
        fields = ['course', 'rating', 'teaching_rating', 'communication_rating', 
                  'engagement_rating', 'comment', 'is_anonymous']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide constructive feedback...'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_teaching_rating(self):
        val = self.cleaned_data.get('teaching_rating')
        return int(val) if val and val != '' else None

    def clean_communication_rating(self):
        val = self.cleaned_data.get('communication_rating')
        return int(val) if val and val != '' else None

    def clean_engagement_rating(self):
        val = self.cleaned_data.get('engagement_rating')
        return int(val) if val and val != '' else None
