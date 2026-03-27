import json
import logging
import multiprocessing

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from query_builder_app.views.sms.sms_service import send_single_sms, send_bulk_sms_from_csv

logger = logging.getLogger(__name__)


@login_required
def sms_home(request):
    return render(request, 'sms/sms.html')


@login_required
@require_POST
def sms_send_single(request):
    """Send a single SMS. Returns JSON response."""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    phone = body.get('phone', '').strip()
    message = body.get('message', '').strip()

    if not phone or not message:
        return JsonResponse({'error': 'Phone and message are required'}, status=400)

    if len(message) > 1600:
        return JsonResponse({'error': 'Message too long (max 1600 chars)'}, status=400)

    try:
        result = send_single_sms(phone, message)
        if result.get('error_code') is None:
            return JsonResponse({
                'status': 'success',
                'message': f'SMS sent to {phone}',
                'sid': result.get('sid', ''),
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': result.get('message', 'Twilio error'),
            }, status=400)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception:
        logger.exception("Error sending single SMS")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_POST
def sms_send_bulk(request):
    """
    Receive a CSV file, kick off bulk SMS sending in a background thread,
    and immediately return a confirmation to the frontend.
    """
    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        return JsonResponse({'error': 'CSV file is required'}, status=400)

    if not csv_file.name.endswith('.csv'):
        return JsonResponse({'error': 'File must be a .csv'}, status=400)

    # Read file content now (before the request closes the file)
    file_content = csv_file.read()

    def _process_bulk(content):
        import io
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backoffice.settings')
        django.setup()
        from query_builder_app.views.sms.sms_service import send_bulk_sms_from_csv as bulk_send
        import logging as _logging
        _logger = _logging.getLogger(__name__)
        try:
            result = bulk_send(io.BytesIO(content))
            _logger.info(
                "Bulk SMS completed: total=%d success=%d failed=%d",
                result['total'], result['success'], result['failed'],
            )
        except Exception:
            _logger.exception("Bulk SMS processing failed")

    process = multiprocessing.Process(target=_process_bulk, args=(file_content,))
    process.start()
    logger.info("Bulk SMS spawned process PID=%d", process.pid)

    return JsonResponse({
        'status': 'success',
        'message': 'Bulk SMS is being processed. Messages will be sent in the background.',
    })
