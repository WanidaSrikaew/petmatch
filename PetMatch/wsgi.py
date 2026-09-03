"""
WSGI config for PetMatch project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PetMatch.settings")

application = get_wsgi_application()
app = application

# Auto-migrate and seed if running in Vercel serverless environment
if "VERCEL" in os.environ:
    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
        call_command("seed_pet_data")
        call_command("collectstatic", interactive=False)
    except Exception as e:
        print("Vercel auto-init notice:", e)
