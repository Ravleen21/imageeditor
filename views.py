from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Image
from .forms import ImageUploadForm
from PIL import Image as PILImage, ImageOps
import os
from django.conf import settings

# Home View
def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            return redirect('my_app:edit_image', image_id=image.id)
    else:
        form = ImageUploadForm()
    images = Image.objects.all()
    return render(request, 'my_app/home.html', {'form': form, 'images': images})


# Upload Image View
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('my_app:home')  # Redirect to the home page after successful upload
    else:
        form = ImageUploadForm()
    return render(request, 'my_app/upload_image.html', {'form': form})


# Edit Image View
def edit_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        pil_image = PILImage.open(image.original_image.path)

        try:
            if action == 'grayscale':
                edited_image = ImageOps.grayscale(pil_image)
            elif action == 'rotate':
                rotate_angle = int(request.POST.get('rotate_angle', 90))  # Default to 90 degrees
                edited_image = pil_image.rotate(rotate_angle, expand=True)
            elif action == 'resize':
                resize_width = int(request.POST.get('resize_width', 300))  # Default width
                resize_height = int(request.POST.get('resize_height', 300))  # Default height
                edited_image = pil_image.resize((resize_width, resize_height))
            else:
                edited_image = pil_image

            # Save the edited image
            edited_dir = os.path.join(settings.MEDIA_ROOT, 'images/edited/')
            os.makedirs(edited_dir, exist_ok=True)  # Ensure the directory exists
            edited_path = os.path.join(edited_dir, f'edited_{image.id}.png')
            edited_image.save(edited_path)
            image.edited_image = f'images/edited/edited_{image.id}.png'
            image.save()
        except Exception as e:
            return HttpResponse(f"Error processing image: {e}")

        return redirect('my_app:edit_image', image_id=image.id)

    return render(request, 'my_app/edit_image.html', {'image': image})


# Download Image View
def download_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if image.edited_image:
        file_path = os.path.join(settings.MEDIA_ROOT, image.edited_image)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="image/png")
                response['Content-Disposition'] = f'attachment; filename="edited_image_{image.id}.png"'
                return response
        else:
            raise Http404("Edited image not found.")
    return HttpResponse("No edited image available.")


# Delete Image View
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.method == 'POST':
        # Delete the image file from the filesystem
        if image.original_image:
            image.original_image.delete()
        if image.edited_image:
            image.edited_image.delete()
        # Delete the image object from the database
        image.delete()
        return redirect('my_app:home')  # Redirect to the home page after deletion
    return render(request, 'my_app/delete_image.html', {'image': image})


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('my_app:home')  # Redirect to the home page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'my_app/login.html')


# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Account created successfully')
            return redirect('my_app:login')  # Redirect to the login page
    return render(request, 'my_app/signup.html')


# Logout View
def logout_view(request):
    logout(request)
    return redirect('my_app:home')  # Redirect to the home page