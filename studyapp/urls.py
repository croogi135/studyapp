from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from allauth.socialaccount import views as socialaccount_views
from . import views

urlpatterns = [
    #path('', TemplateView.as_view(template_name="index.html"), name='home'),
    path('', views.index, name='home'),
    #path('login', TemplateView.as_view(template_name="login.html"), name='login'),
    #path('map', TemplateView.as_view(template_name="map.html"), name='map'),
    path('map', views.map_view, name='map'),
    path('accounts/', include('allauth.urls')),
    # path('social/signup/', views.signup_redirect, name='signup_redirect'),
    path('logout', LogoutView.as_view()),
    path('reviews/', views.ReviewApproval.as_view(), name='review_approval'),
    path('submissions/', views.StudySpotListView.as_view(), name='studyspot_list'),
    path('logout', views.logout_view, name='logout'),
    path('submit', views.spot_create_view.as_view(),name='submit'),
    path('building/<str:building_name>/', views.building_detail, name='building_detail'),
    path('mapsubmit', TemplateView.as_view(template_name="location_submission.html"), name='map submit'),
]