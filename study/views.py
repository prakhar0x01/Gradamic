from django.shortcuts import render
from .models import Study
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os

@login_required
def material_detail(request, pk):
    study_material = get_object_or_404(Study, pk=pk)
    pdf_path = os.path.basename(study_material.notes_pdf.path)
    print(pdf_path)
    return render(request, 'material_detail.html', {'study_material': study_material, 'pdf_path': pdf_path})


def materials_list(request):
    study_materials = Study.objects.all()
    return render(request, 'materials_list.html', {'study_materials': study_materials})


@login_required
def download_notes(request, pk):
    study_material = get_object_or_404(Study, pk=pk)
    file_path = os.path.join(settings.MEDIA_ROOT, str(study_material.notes_pdf))
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        filename = os.path.basename(study_material.notes_pdf.name)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response