from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

def detect_leaf_page(request):
    if request.method == 'POST' and request.FILES.get('leaf_image'):
        leaf_image = request.FILES['leaf_image']

        # Simpan file ke media folder biar bisa diakses
        fs = FileSystemStorage()
        filename = fs.save(leaf_image.name, leaf_image)
        uploaded_file_url = fs.url(filename)

        # Simulasi hasil deteksi
        context = {
            'uploaded_file_url': uploaded_file_url,
            'detected_pest': 'Ulat Grayak',
            'confidence': 92,
            'severity': 'Sedang',
        }
        return render(request, 'detection/detect_leaf.html', context)

    # kalau belum upload, kirim template kosong
    return render(request, 'detection/detect_leaf.html')
