from django.contrib import admin
from .models import *


@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    search_fields = ['nom', 'prenom']
admin.site.register(Formation)
admin.site.register(Action)
admin.site.register(AssignerA)
admin.site.register(SInscrire)
admin.site.register(Salle)
admin.site.register(Reunion)
admin.site.register(SupportDeCours)
admin.site.register(Utiliser)
admin.site.register(ProcesRendu)
admin.site.register(Organiser)
admin.site.register(Decision)
admin.site.register(Assister)
