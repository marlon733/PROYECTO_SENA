from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.

  
@login_required
def productos(request):
    return render(request, 'producto.html')