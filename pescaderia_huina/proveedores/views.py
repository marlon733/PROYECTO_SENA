from django.shortcuts import render

from django.shortcuts import render

def agregar_proveedor(request):
    # Asegúrate de que el nombre del archivo coincida exactamente con tu carpeta templates
    return render(request, 'agregar_proveedor.html')