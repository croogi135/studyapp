from statistics import mean

from django.db import models
from django.utils import timezone

# Create your models here.
class School(models.TextChoices):
    arts_and_sci = 'Arts and Sciences'
    business = 'Business'
    politics = 'Leadership and Public Policy'
    commerce = 'Commerce'
    architecture = 'Architecture'
    edu = 'Education and Human Development'
    engr = 'Engineering and Applied Science'
    law = 'Law'
    med = 'Medicine'
    nurse = 'Nursing'


class User(models.Model):
    email = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    school = models.CharField(max_length=50, choices=School.choices)


class StudySpot(models.Model):
    building = models.CharField(max_length=100)
    room_number = models.CharField(max_length=5, blank=True, null=True)
    lat = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)
    lng = models.DecimalField(max_digits=20, decimal_places=15, blank=True, null=True)

    # hidden features, not included in user submission page
    submitted_by = models.ForeignKey(User, models.CASCADE)
    is_approved = models.BooleanField(default=False)
    submission_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f'{self.building} {self.room_number}'

    def print_submission_user(self):
        return f'Submission by {self.submitted_by}'

    def get_overall_rating(self):
        reviews = Review.objects.filter(location=self)
        if reviews:
            return mean([review.rating for review in reviews])
        else:
            return 0

PARKING_CHOICES = [
    ('Street', 'Street'),
    ('Garage', 'Garage'),
    ('Parking lot', 'Parking lot'),
    ('None', 'None'),
]
HOUR_CHOICES = [
    ('Open Late', 'Open Late'),
    ('24/7', '24/7'),
    ('Normal Hours', 'Normal Hours'),
    ('Closes early', 'Closes early'),
]
class Review(models.Model):
    RATING_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    building = models.CharField(max_length=100,default='')
    room_number = models.CharField(max_length=5, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    noise_level = models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    crowdedness =models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    comfort =models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    location =models.PositiveSmallIntegerField(choices=RATING_CHOICES)

    parking = models.CharField(
        max_length=20,
        choices=PARKING_CHOICES,
        default='Garage',blank=True, null=True
    )
    hours =  models.CharField(
        max_length=20,
        choices=HOUR_CHOICES,
        default='Normal Hours',blank=True, null=True
    )
    occupancy = models.IntegerField( blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
