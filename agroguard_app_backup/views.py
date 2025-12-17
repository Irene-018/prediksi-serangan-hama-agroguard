from django.shortcuts import render, get_object_or_404
from .models import DetectionResult, PesticideRecommendation, DosageInstruction, PestTips, FilesResource

# ============================
# HALAMAN RIWAYAT DETEKSI
# ============================
def riwayat(request):
    user_id = request.user.id  

    riwayat_list = DetectionResult.objects.filter(
        user_id=user_id
    ).order_by('-detected_at')

    return render(request, "dashboard/riwayat.html", {"riwayat": riwayat_list})


# ============================
# HALAMAN DETAIL REKOMENDASI
# ============================
def recommendation_detail(request, detection_id):

    detection = get_object_or_404(DetectionResult, pk=detection_id)

    pesticides = PesticideRecommendation.objects.filter(detection=detection)
    dosage = DosageInstruction.objects.filter(detection=detection).first()
    tips = PestTips.objects.filter(detection=detection)
    resources = FilesResource.objects.filter(detection=detection).first()

    context = {
        "det": detection,
        "pesticides": pesticides,
        "dosage": dosage,
        "tips": tips,
        "resources": resources,
    }

    return render(request, "dashboard/detail_rekomendasi.html", context)
