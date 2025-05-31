from django.urls import path
from . import views

urlpatterns = [  

    path('api/formations/search/', views.search_formations, name='search_formations'),
    path('api/reunions/search/', views.search_reunions, name='search_reunions'),

    path('detail_reunion_fr/<int:id>',views.detail_reunion_frt,name='detail_reunion_frt'),
    path('page_reunions/',views.page_reunion,name='page_reunions'),
    path('',views.index,name='home'),
    path('deconnexion/',views.deconnexion,name='deconnexion'),
    path('detail_reunion/<int:id>',views.detail_reunion,name='detail_reunion'),
    path('detail_formation/<int:id>',views.detail_formation,name='detail_formation'),
    path('formations/',views.formations,name='formations'),
    path('mes_taches/' ,views.mes_taches,name='mes_taches'),
    path('connexion/',views.connexion,name='connexion'),
    path('deconnexion/',views.deconnexion,name='deconnexion'),
    path('creer_compte/',views.creer_compte,name='creer_compte'),
    path('inscription/',views.inscription,name='inscription'),
    
    path('administration/',views.administration,name='administration'),
    path('administration/editer_formation/<int:id>',views.editer_formation,name='editer'),
    path('administration/supprimer_reunion/<int:id>',views.supprimer_reunion,name='supprimer_reunion'),
    path('administration/editer_reunion/<int:id>',views.editer_reunion,name='editer_reunion'),
    path('administration/afficher_formations_reunion',views.afficher_formations_reunions,name='formations_reunions'),
    path('administration/supprimer/<int:id>',views.supprimer,name='supprimer'),
    path('administration/rediger_pv',views.rediger_pv,name='rediger_pv'),
    path('administration/afficher/<int:id>',views.afficher,name='afficher'),
    path('administration/planifier_evenement/',views.planifierEvent,name='planifier_evenement'),
    path('administration/planifier_formation/',views.planifier_formation,name='planifier_formation'),
    path('administration/planifier_reunion/',views.planifier_reunion,name='planifier_reunion'),
    path('administration/planifier_decision/',views.planifier_decision,name='planifier_decision'),
    path('administration/planifier_action/',views.planifier_action,name='planifier_action'),
    path('administration/suivi_decision/',views.suivreDecision,name='suivre'),
    path('administration/profil/',views.profil_util,name='profil_util'),
    path('administration/editer_profil/',views.editer_profil,name='editer_profil'),
    path('administration/afficher_profil/<int:id>',views.afficher_profil,name='afficher_profil'),
    path('administration/afficher_reunion/<int:id>',views.afficher_reunion,name='afficher_reunion'),
    path('administration/afficher_actions_decisions/',views.afficher_actions_decisions,name='afficher_actions_decisions'),
    path('administration/afficher_decision/<int:id>',views.afficher_decision,name='afficher_decision'),
    path('administration/afficher_action/<int:id>',views.afficher_action,name='afficher_action'),
    path('administration/reporting',views.reporting,name='reporting'),
    path('administration/televerserSupports/',views.televerserSupports,name='televerserSupports'),

    
    
]
