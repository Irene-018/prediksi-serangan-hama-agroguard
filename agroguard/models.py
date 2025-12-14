from django.db import models

class DetectionResult(models.Model):
    user_id = models.IntegerField(null=True, blank=True)
    plant_name = models.CharField(max_length=100)
    pest_name = models.CharField(max_length=100)
    severity_level = models.CharField(max_length=50)
    scientific_name = models.CharField(max_length=150, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    image_path = models.CharField(max_length=255)
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pest_name} - {self.detected_at}"
    

class PesticideRecommendation(models.Model):
    detection = models.ForeignKey(DetectionResult, on_delete=models.CASCADE)
    option_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.option_name}"


class DosageInstruction(models.Model):
    detection = models.ForeignKey(DetectionResult, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    spray_volume = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    interval_days = models.IntegerField()
    pre_harvest_interval = models.IntegerField()

    def __str__(self):
        return f"Dosis untuk {self.detection.pest_name}"


class PestTips(models.Model):
    detection = models.ForeignKey(DetectionResult, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    content = models.TextField()

    def __str__(self):
        return f"{self.category}"


class FilesResource(models.Model):
    detection = models.ForeignKey(DetectionResult, on_delete=models.CASCADE)
    pdf_path = models.CharField(max_length=255)
    youtube_url = models.CharField(max_length=255)

    def __str__(self):
        return f"File {self.detection.pest_name}"
