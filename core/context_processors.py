from .models import SiteSetting

def site_settings(request):
    """
    Exposes the site setting object to all templates.
    """
    settings = SiteSetting.objects.first()
    return {'site_settings': settings}
