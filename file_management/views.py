# file_management/views.py

import os
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
import paramiko
from file_management.forms import FileUploadForm
from file_management.models import MailingFactory
from crispy_forms.helper import FormHelper


def mailing_factory_list(request):
    mailing_factories = MailingFactory.objects.all()
    form = FileUploadForm()
    crispy_form = FormHelper(form)
    return render(request, 'list.html', {
        'mailing_factories': mailing_factories,
        'form': form,
        "crispy": crispy_form
    })

def mailing_factory_create(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Crea la instancia pero no la guardes aún para poder modificar algunos campos manualmente
            mailing_factory_instance = form.save(commit=False)
            
            # Suponiendo que quieres establecer el nombre del archivo subido como file_name
            # Asegúrate de que el campo 'file' existe en tu form y se refiere al archivo subido
            if 'file' in request.FILES:
                type = request.POST.get('type')
                if type == 'header':
                    prefix = 'h'
                elif type == 'body':
                    prefix = 'b'
                elif type == 'footer':
                    prefix = 'f'
                else:
                    prefix = ''
                    
                white_label = request.POST.get('white_label')
                file_name = request.POST.get('name')

                extension = os.path.splitext(request.FILES['file'].name)[1]

                file_name_server = white_label + '-' + prefix + '-' + file_name + extension
                handle_uploaded_file(request.FILES['file'], file_name_server)
                transferir_archivo_via_scp(file_name_server)
                # delete_local_file(file_name_server)
                mailing_factory_instance.extension = extension
                mailing_factory_instance.file_name = prefix + '-' + file_name
        
            # Guarda la instancia en la base de datos. Esto insertará el registro.
            mailing_factory_instance.save()
            
            # Ahora puedes redirigir al usuario a la lista de elementos o a cualquier otra página
            return redirect('mailing_factory_list')
        else:
            # Si el formulario no es válido, podrías querer enviar de vuelta al usuario al formulario con los errores mostrados
            return render(request, 'create-form.html', {'form': form})




def mailing_factory_update(request, pk):
    mailing_factory = get_object_or_404(MailingFactory, pk=pk)
    if request.method == 'POST':
        white_label = request.POST.get('white_label')
        name = request.POST.get('name')
        type = request.POST.get('type')
        campaign = request.POST.get('campaign')
        permanent = request.POST.get('permanent')
        file_name = request.FILES.get('file_name')
        href = request.POST.get('href')
        mailing_factory.white_label = white_label
        mailing_factory.name = name
        mailing_factory.type = type
        mailing_factory.campaign = campaign
        mailing_factory.permanent = permanent
        mailing_factory.file_name = file_name
        mailing_factory.href = href
        mailing_factory.save()
        return JsonResponse({'success': True, 'message': 'Mailing factory updated successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def mailing_factory_delete(request, pk):
    mailing_factory = get_object_or_404(MailingFactory, pk=pk)
    if request.method == 'POST':
        mailing_factory.delete()
        return JsonResponse({'success': True, 'message': 'Mailing factory deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def about(request):
    return render(request, 'mailing_factory/templates/about.html')


def handle_uploaded_file(f, name):
    with open('uploads/' + name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def delete_local_file(nombre_archivo):
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', nombre_archivo)
    os.remove(local_path)

def transferir_archivo_via_scp(nombre_archivo):


    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', nombre_archivo)
    # Obtener credenciales y detalles del servidor de las variables de entorno
    ssh_host = os.environ.get('SSH_HOST', 'platform.multikrd.com')
    ssh_port = int(os.environ.get('SSH_PORT', 2201))
    ssh_user = os.environ.get('SSH_USER')
    ssh_password = os.environ.get('SSH_PASSWORD')

    # Crear una instancia de SSHClient
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Establecer conexión SSH
        ssh.connect(hostname=ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)
        
        # Iniciar sesión SFTP
        sftp = ssh.open_sftp()
        
        # Ruta remota donde se guardará el archivo
        remote_path = "" # f"/var/www/mailing/files/{nombre_archivo}"
        
        # Transferir el archivo
        sftp.put(local_path, remote_path)

        # Cerrar conexión SFTP y SSH
        sftp.close()
        ssh.close()
        
        print("Archivo transferido con éxito.")
    except Exception as e:
        print(f"Error al transferir el archivo: {str(e)}")
