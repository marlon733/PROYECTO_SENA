from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def login(request):
  template = loader.get_template('core/login.html')
  return HttpResponse(template.render())

def restablecer(request):
  template = loader.get_template('core/restablecer.html')
  return HttpResponse(template.render())

def PanelAdmin_base(request):
    return render(request, 'core/panel_admin_base.html')

def producto(request):
    return render(request, 'producto.html')