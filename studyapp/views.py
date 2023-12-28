from typing import Any
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .models import StudySpot, User, Review
from .forms import UserForm, StudySpotForm, ReviewForm, ApprovalForm
from django.views.generic import CreateView
from django.db import transaction
from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import StudySpot, Review
from django.db.models import Avg, Q, Count
def building_detail(request, building_name):
    avg_ratings=Review.objects.filter(
        Q(building=building_name, is_approved=True),
        Q(room_number__isnull=True) | Q(room_number__exact='') | Q(room_number__regex=r'^[^\d]*$')
    ).aggregate(
        Avg('rating'), Avg('noise_level'), Avg('crowdedness'), Avg('comfort'), Avg('location')
    )
    avg_ratings = {key: round(value, 2) if value is not None else None for key, value in avg_ratings.items()}

    parking_count = Review.objects.filter(building=building_name, is_approved=True).values('parking').annotate(count=Count('parking')).order_by('-count')
    hours_count = Review.objects.filter(building=building_name, is_approved=True).values('hours').annotate(count=Count('hours')).order_by('-count')
    
    occupan = Review.objects.filter(building=building_name, is_approved=True).values('occupancy')
    descrip = Review.objects.filter(
        Q(building=building_name, is_approved=True),
        Q(room_number__isnull=True) | Q(room_number__exact='') | Q(room_number__regex=r'^[^\d]*$')
    ).values('description')
    
    most_common_parking = parking_count.first()['parking'] if parking_count.exists() else None
    most_common_hours = hours_count.first()['hours'] if hours_count.exists() else None
    
    rooms = Review.objects.filter(
        Q(building=building_name, is_approved=True),
        ~Q(room_number__isnull=True),
        ~Q(room_number__exact=''),
        ~Q(room_number__regex=r'^[^\d]*$')
    ).values('room_number').distinct()
    
    room_data = []
    for room in rooms:
        room_number = room['room_number']
        room_reviews = Review.objects.filter(building=building_name, room_number=room_number, is_approved=True)
        room_avg_ratings = room_reviews.aggregate(
            Avg('rating'), Avg('noise_level'), Avg('crowdedness'), Avg('comfort'), Avg('location')
        )
        room_avg_ratings = {key: round(value, 2) if value is not None else None for key, value in room_avg_ratings.items()}
        room_description= Review.objects.filter(building=building_name, room_number=room_number, is_approved=True).values('description')
        room_data.append({
            'room_number': room_number,
            'reviews': room_reviews,
            'avg_ratings': room_avg_ratings,   
            'room_description': room_description     
        })
    
    context = {
        'building_name': building_name,
        'avg_ratings': avg_ratings,
        'room_data': room_data,
        'most_common_parking': most_common_parking,
        'most_common_hours': most_common_hours, 
        'description': descrip,
    }

    return render(request, 'building_detail.html', context)
class ReviewApproval(ListView):
    model = Review
    template_name = 'studyapp/reviewapprove.html'
    context_object_name = 'reviews'
    queryset = Review.objects.filter(is_approved=False)

    def post(self, request, *args, **kwargs):
        if self.request.POST:
            for key in self.request.POST:
                if key.startswith('approve_review_'):
                    review_id = key.split('_')[2]
                    try:
                        review = Review.objects.get(id=review_id)
                        review.building = request.POST.get(f'building_{review_id}')
                        review.room_number = request.POST.get(f'room_number_{review_id}')
                        review.is_approved = True
                        review.save()
                        messages.success(request, 'Selected reviews have been approved!')
                    except Review.DoesNotExist:
                        messages.error(request, 'Review not found')
                    except Exception as e:
                        messages.error(request, f'Error approving review: {str(e)}')

            return redirect('review_approval')


class StudySpotListView(ListView):
    model = StudySpot
    template_name = 'studyapp/studyspots_list.html'
    context_object_name = 'studyspots'
    queryset = StudySpot.objects.filter(is_approved=False)

    def post(self, request, *args, **kwargs):
        if self.request.POST:
            for key in self.request.POST:
                if key.startswith('approve_'):
                    studyspot_id = key.split('_')[1]
                    try:
                        studyspot = StudySpot.objects.get(id=studyspot_id)
                        studyspot.building = request.POST.get(f'building_{studyspot_id}')
                        studyspot.room_number = request.POST.get(f'room_number_{studyspot_id}')
                        studyspot.is_approved = True
                        studyspot.save()
                        messages.success(request, 'Selected StudySpots have been approved!')
                    except StudySpot.DoesNotExist:
                        messages.error(request, 'StudySpot not found')
                    except Exception as e:
                        messages.error(request, f'Error approving StudySpot: {str(e)}')
            return redirect('studyspot_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unique_buildings = StudySpot.objects.filter(is_approved=True).order_by('building').distinct('building')
        approved_spots = StudySpot.objects.filter(is_approved=True).values('building', 'lat', 'lng')
        unapproved_spots = StudySpot.objects.filter(is_approved=False).values('building', 'lat', 'lng')

        unique_lat_lng = {}
        for spot in approved_spots:
            unique_key = f"{spot['building']}_{spot['lat']}_{spot['lng']}"
            if unique_key not in unique_lat_lng:
                spot['lat'] = float(spot['lat'])
                spot['lng'] = float(spot['lng'])
                unique_lat_lng[unique_key] = spot

        unique_lat_lng_data = list(unique_lat_lng.values())
        unique_spots_json = json.dumps(unique_lat_lng_data, cls=DjangoJSONEncoder)
        unapproved_spots_data = list(unapproved_spots)
        unapproved_spots_json = json.dumps(unapproved_spots_data, cls=DjangoJSONEncoder)

        context['unique_spots_json'] = unique_spots_json
        context['unapproved_spots'] = unapproved_spots_json
        context['unique_buildings'] = unique_buildings

        return context

def index(request):
    spots = StudySpot.objects.filter(is_approved=True)
    return render(request, 'index.html',{'spots':spots})

def map_view(request):
    unique_buildings = StudySpot.objects.filter(is_approved=True).order_by('building').distinct('building')
    unique_lat_lng = {}

    for building in unique_buildings:
        avg_ratings = Review.objects.filter(
        Q(building=building.building, is_approved=True),
        Q(room_number__isnull=True) | Q(room_number__exact='') | Q(room_number__regex=r'^[^\d]*$')
    ).aggregate(
        Avg('rating'), Avg('noise_level'), Avg('crowdedness'), Avg('comfort'), Avg('location')
    )
        unique_key = f"{building.building}_{building.lat}_{building.lng}"
        if unique_key not in unique_lat_lng:
            unique_lat_lng[unique_key] = {
                'building': building.building,
                'lat': float(building.lat),
                'lng': float(building.lng),
                'avg_ratings': avg_ratings,
            }

    unique_lat_lng_data = list(unique_lat_lng.values())
    unique_spots_json = json.dumps(unique_lat_lng_data, cls=DjangoJSONEncoder)
    context = {
        'unique_spots_json': unique_spots_json,
        'unique_buildings': unique_buildings,
        'unique_lat_lng': unique_lat_lng,
    }
    return render(request, 'map.html', context)


def view_submissions(request):
    approved_submissions = StudySpot.objects.filter(is_approved=True)
    return render(request, 'studyapp/studyspots_list.html', {'locations': approved_submissions})


def approve_submission(request, sub_id):
    study_spot = get_object_or_404(StudySpot, id=sub_id)

    if request.method == 'POST':
        study_spot.is_approved = True
        study_spot.save()
        HttpResponse("Study spot approved successfully.")

    return render(request, 'studyapp/studyspots_component.html', {'studyspot': study_spot})


def logout_view(request):
    logout(request)
    return redirect('home')


@staff_member_required()
def submission_component(request, sub_id):
    studyspot = get_object_or_404(StudySpot, id=sub_id)
    return render(request, 'admin/submission_component.html', {'studyspot': studyspot})


def update_submission(request, sub_id):
    study_spot = get_object_or_404(StudySpot, id=sub_id)

    if request.method == 'POST':
        post = request.POST
        study_spot.building = post.get('building')
        study_spot.room_number = post.get('room_number')
        study_spot.save()

    return render(request, 'studyapp/submission_component.html', {'studyspot': study_spot})


class register__create_view(CreateView):
    model = User
    form_class = UserForm
    
class spot_create_view(CreateView):
    model = StudySpot
    form_class = StudySpotForm
    template_name = "submission.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        unique_buildings = StudySpot.objects.filter(is_approved=True).order_by('building').distinct('building')
        approved_spots = StudySpot.objects.filter(is_approved=True).values('building', 'lat', 'lng')
        unique_lat_lng = {}
        for spot in approved_spots:
            unique_key = f"{spot['building']}_{spot['lat']}_{spot['lng']}"
            if unique_key not in unique_lat_lng:
                spot['lat'] = float(spot['lat'])
                spot['lng'] = float(spot['lng'])
                unique_lat_lng[unique_key] = spot

        unique_lat_lng_data = list(unique_lat_lng.values())
        unique_spots_json = json.dumps(unique_lat_lng_data, cls=DjangoJSONEncoder)

        # Include map data in the context
        context['unique_spots_json'] = unique_spots_json
        context['unique_buildings'] = unique_buildings
        context['unique_lat_lng'] = unique_lat_lng        
        if self.request.POST:
            #Need to define form/formset in forms.py:
            context['spot_form'] = StudySpotForm(self.request.POST)
            context['review_form'] = ReviewForm(self.request.POST)
        else:
            context['spot_form'] = StudySpotForm()
            context['review_form'] = ReviewForm()
        return context
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        spot_form = StudySpotForm(self.request.POST)
        review_form = ReviewForm(self.request.POST)  # Create an instance of the ReviewForm

        if form.is_valid() and spot_form.is_valid():
            # Handle the StudySpot creation
            self.object = form.save(commit=False)
            self.object.pub_date = timezone.now()
            self.object.is_approved = False
            self.object.submitted_by = User.objects.create(email="cs3240.student@gmail.com", username="common_user", first_name="Test", last_name="User", school="Engineering and Applied Science")
            self.object.lat = float(spot_form.cleaned_data['lat'])
            self.object.lng = float(spot_form.cleaned_data['lng'])
            self.object.save()
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.building = self.object.building
                review.room_number = self.object.room_number
                review.save()

            return self.form_valid(form, spot_form)
        else:
            return self.form_invalid(form, spot_form)
    def form_invalid(self, form, spot_form):
        messages.error(self.request, 'Error: Please fix the form errors.')
        return self.render_to_response(
            self.get_context_data(form=form, spot_form=spot_form)
        )
    def form_valid(self, form,spot_form):
        self.object = form.save(commit=False)
        self.object.pub_date = timezone.now()
        self.object.is_approved = False
        self.object.submitted_by = User.objects.create(email="cs3240.student@gmail.com", username="common_user",first_name="Test", last_name="User",school="Engineering and Applied Science")
        self.object.lat = float(spot_form.cleaned_data['lat'])
        self.object.lng = float(spot_form.cleaned_data['lng'])
        self.object.save()

        review_form = ReviewForm(self.request.POST)
        if review_form.is_valid():
            self.object.save()
            review = review_form.save(commit=False)
            review.building = self.object.building
            review.room_number = self.object.room_number
            messages.success(self.request, 'Success: Spot and review submitted successfully!')
            return redirect(reverse('submit'))
        else:
            messages.error(self.request, 'Error: Please fix the review form errors.')
            return self.render_to_response(
                self.get_context_data(form=form, spot_form=spot_form, review_form=review_form)
            )
        
    def form_invalid(self, form, spot_form):
        return self.render_to_response(
            self.get_context_data(form=form, spot_form=spot_form)
        )

