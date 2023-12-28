from django import forms
from django.forms import HiddenInput, ModelForm, ValidationError

from studyapp.widgets import StarRatingSelect
from .models import User, StudySpot, Review


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class StudySpotForm(ModelForm):
    lat = forms.FloatField(widget=HiddenInput, required=False)
    lng = forms.FloatField(widget=HiddenInput, required=False)
    building = forms.CharField(label='Building Name', error_messages={'required': 'Building name is required.'})
    room_number = forms.CharField(label='Room Number (Optional)', required=False)

    class Meta:
        model = StudySpot
        fields = ['building', 'room_number']

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')

        if lat is None or lng is None:
            self.add_error(None, 'Please choose a spot on the map.')

        return cleaned_data

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'noise_level', 'crowdedness', 'comfort', 'location', 'parking','hours', 'occupancy', 'description']
        widgets = {
            'rating': StarRatingSelect(),
            'noise_level': StarRatingSelect(),
            'crowdedness': StarRatingSelect(),
            'comfort': StarRatingSelect(),
            'location': StarRatingSelect(),
        }
        
    occupancy = forms.IntegerField(label='Occupancy (Optional)', required=False)
    description=forms.CharField(label='Description (Optional)', required=False)
    
class ApprovalForm(ModelForm):
    spot_id = forms.IntegerField()
