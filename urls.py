from django.urls import path
from . import views

app_name = 'my_app'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Edit an image by its ID
    path('edit/<int:image_id>/', views.edit_image, name='edit_image'),
    
    # Download an image by its ID
    path('download/<int:image_id>/', views.download_image, name='download_image'),
    
    # Upload a new image
    path('upload/', views.upload_image, name='upload_image'),
    
    # Delete an image by its ID
    path('delete/<int:image_id>/', views.delete_image, name='delete_image'),
    
    # Login page
    path('login/', views.login_view, name='login'),
    
    # Signup page
    path('signup/', views.signup_view, name='signup'),
    
    # Logout functionality
    path('logout/', views.logout_view, name='logout'),
]