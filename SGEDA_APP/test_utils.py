from django.apps import apps
from .models import Salle

def get_next_pk(model_name):
    """Retourne le prochain ID disponible pour un modèle"""
    model = apps.get_model('sgeda_app', model_name)
    last_obj = model.objects.order_by('-id').first()
    return last_obj.id + 1 if last_obj else 1

def get_next_salle_numero():
    """Retourne le prochain numéro de salle disponible"""
    last_salle = Salle.objects.order_by('-numero').first()
    return last_salle.numero + 1 if last_salle else 101