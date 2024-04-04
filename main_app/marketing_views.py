from django.shortcuts import render


def marketing_files(request):
    # files = os.listdir('/path/to/marketing/files')  # Replace '/path/to/marketing/files' with the actual path to the marketing files directory
    return render(request, 'marketing/files.html', {'files': None})

