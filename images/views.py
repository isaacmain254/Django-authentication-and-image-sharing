from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from django.http import  JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action

# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent 
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, "Image added successfully")

            # redirect to new created item detail view
            return redirect(new_image.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})

# image detail view
def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request, 'images/image/detail.html', {"section": "images", "image": image})

# like and unlike action view
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.user_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.user_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


# image list view
@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # if AJAX request and page out of range
            # return the empty page
            return HttpResponse('')
        # if page is out of range return the last page of the results
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html',
         {'section': 'images', 'images': images})
    
    return render(request, 'images/image/list.html',
     {'section': 'images', 'images': images})