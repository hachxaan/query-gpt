# file_management/views.py

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import FileUploadForm
from .models import FilesModel
import os

@csrf_exempt
def list_files(request):
    files = FilesModel.objects.all()  # Recupera todos los archivos
    return render(request, 'file_management/list_files.html', {'files': files})

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Guarda la información del archivo en la base de datos
            file_instance = form.save(commit=False)
            file_instance.name = request.FILES['file'].name
            file_instance.save()
            # Guarda el archivo en el sistema de archivos del servidor
            handle_uploaded_file(request.FILES['file'])
            return redirect('list_files')  # Redirige a una página de éxito
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

def handle_uploaded_file(f):
    with open('uploads/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def download_file(request, file_id):
    file_instance = FilesModel.objects.get(id=file_id)
    file_path = 'uploads/' + file_instance.name
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type="image/png")
        response['Content-Disposition'] = 'attachment; filename=' + file_instance.name
        return response

@csrf_exempt
def delete_file(request, file_id):
    file_instance = FilesModel.objects.get(id=file_id)
    file_path = 'uploads/' + file_instance.name
    if os.path.isfile(file_path):
        os.remove(file_path)
    file_instance.delete()
    return redirect('list_files')  # Redirige a una página de éxito después de borrar
