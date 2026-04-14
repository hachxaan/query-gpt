import csv
import io
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from query_builder_app.helpers.catalogs import (
    get_exclusions,
    get_exclusion_by_id,
    add_exclusion,
    update_exclusion,
    delete_exclusion,
    bulk_add_exclusions,
    bulk_delete_exclusions,
    search_companies,
)

logger = logging.getLogger(__name__)


@login_required
def exclusion_list(request):
    """List all companies in the mailing exclusion catalog."""
    search = request.GET.get('search', '').strip()
    try:
        exclusions = get_exclusions(search=search if search else None)
    except Exception as e:
        logger.exception("Error fetching exclusions")
        exclusions = []
        messages.error(request, f"Error loading data: {e}")
    return render(request, 'catalogs/exclusion_list.html', {
        'exclusions': exclusions,
        'search': search,
    })


@login_required
@require_http_methods(["POST"])
def exclusion_add(request):
    """Add a single company to the exclusion list."""
    company_id = request.POST.get('company_id', '').strip()
    reason = request.POST.get('reason', '').strip() or None

    if not company_id or not company_id.isdigit():
        messages.error(request, "Invalid company ID.")
        return redirect('exclusion_list')

    try:
        result = add_exclusion(int(company_id), reason)
        if result:
            messages.success(request, f"Company {company_id} added to exclusion list.")
        else:
            messages.warning(request, f"Company {company_id} is already in the exclusion list.")
    except Exception as e:
        logger.exception("Error adding exclusion")
        messages.error(request, f"Error: {e}")

    return redirect('exclusion_list')


@login_required
@require_http_methods(["POST"])
def exclusion_update(request, pk):
    """Update the reason of an exclusion."""
    reason = request.POST.get('reason', '').strip() or None
    try:
        if update_exclusion(pk, reason):
            messages.success(request, "Exclusion updated.")
        else:
            messages.error(request, "Exclusion not found.")
    except Exception as e:
        logger.exception("Error updating exclusion")
        messages.error(request, f"Error: {e}")
    return redirect('exclusion_list')


@login_required
@require_http_methods(["POST"])
def exclusion_delete(request, pk):
    """Delete a single exclusion."""
    try:
        if delete_exclusion(pk):
            messages.success(request, "Exclusion removed.")
        else:
            messages.error(request, "Exclusion not found.")
    except Exception as e:
        logger.exception("Error deleting exclusion")
        messages.error(request, f"Error: {e}")
    return redirect('exclusion_list')


@login_required
@require_http_methods(["POST"])
def exclusion_bulk_delete(request):
    """Bulk delete selected exclusions."""
    ids = request.POST.getlist('selected_ids')
    if not ids:
        messages.warning(request, "No records selected.")
        return redirect('exclusion_list')

    try:
        int_ids = [int(i) for i in ids]
    except ValueError:
        messages.error(request, "Invalid selection.")
        return redirect('exclusion_list')

    try:
        count = bulk_delete_exclusions(int_ids)
        messages.success(request, f"{count} exclusion(s) removed.")
    except Exception as e:
        logger.exception("Error bulk deleting exclusions")
        messages.error(request, f"Error: {e}")
    return redirect('exclusion_list')


@login_required
@require_http_methods(["POST"])
def exclusion_bulk_add(request):
    """
    Bulk add exclusions from CSV upload.
    Expected CSV format: company_id,reason (header optional)
    """
    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        messages.error(request, "No file uploaded.")
        return redirect('exclusion_list')

    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Please upload a CSV file.")
        return redirect('exclusion_list')

    try:
        decoded = csv_file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(decoded))
        entries = []
        for i, row in enumerate(reader):
            if not row:
                continue
            # Skip header row
            if i == 0 and row[0].lower().strip() in ('company_id', 'id'):
                continue
            company_id = row[0].strip()
            if not company_id.isdigit():
                continue
            reason = row[1].strip() if len(row) > 1 and row[1].strip() else None
            entries.append((int(company_id), reason))

        if not entries:
            messages.warning(request, "No valid entries found in CSV.")
            return redirect('exclusion_list')

        count = bulk_add_exclusions(entries)
        messages.success(request, f"{count} exclusion(s) added from CSV ({len(entries)} processed).")
    except Exception as e:
        logger.exception("Error bulk adding exclusions")
        messages.error(request, f"Error processing CSV: {e}")

    return redirect('exclusion_list')


@login_required
def company_search_api(request):
    """API endpoint for company autocomplete search."""
    term = request.GET.get('term', '').strip()
    if len(term) < 2:
        return JsonResponse([], safe=False)
    try:
        results = search_companies(term)
        return JsonResponse(results, safe=False)
    except Exception as e:
        logger.exception("Error searching companies")
        return JsonResponse([], safe=False)
