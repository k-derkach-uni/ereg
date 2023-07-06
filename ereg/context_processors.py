from django.conf import settings


def polyclinic_name(request):
    return {
        'POLYCLINIC_NAME': settings.POLYCLINIC_NAME,
    }
