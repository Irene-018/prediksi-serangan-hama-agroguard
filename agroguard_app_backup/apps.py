from django.apps import AppConfig
from django.shortcuts import render, get_object_or_404

class AgroguardAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agroguard_app'


def recommendation_detail(request, detection_id):
    detection = get_object_or_404(DetectionResult, id=detection_id)

    pesticides = PesticideRecommendation.objects.filter(detection_id=detection_id)
    dosages = DosageInstruction.objects.filter(detection_id=detection_id)
    tips = PestTips.objects.filter(detection_id=detection_id)
    files = FilesResource.objects.filter(detection_id=detection_id)

    context = {
        "detection": detection,
        "pesticides": pesticides,
        "dosages": dosages,
        "tips": tips,
        "files": files,
    }
    return render(request, "recommendation.html", context)
