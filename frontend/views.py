from django.shortcuts import render

def welcome(request):
    return render(request, "welcome.html")

def deteksi(request):
    return render(request, "deteksi.html")

def rekomendasi(request):
    return render(request, "rekomendasi.html")

def riwayat(request):
    return render(request, "riwayat.html")

def profile(request):
    return render(request, "profile.html")
