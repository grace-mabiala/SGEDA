from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Formation,Utilisateur,Salle,Decision,Action,Reunion,AssignerA,SupportDeCours,SInscrire,Assister
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.shortcuts import render
import os
from django.conf import settings
from django.contrib.auth import  login,logout
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote
from django.views.decorators.http import require_POST
import json
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def index(request):
    return render(request,'sgeda/home/index.html')

def connexion(request):
    if request.method == 'POST':
        email = request.POST['email']
        mot_de_passe = request.POST['password']
        try:
            utilisateur = Utilisateur.objects.get(email=email, mot_de_passe=mot_de_passe)
            print(utilisateur)
            # Store user information in session
            # request.session['user_id'] = utilisateur.id
            # request.session['user_email'] = utilisateur.email
            login(request, utilisateur)
            messages.success(request, "Connexion réussie!")
            return redirect('home')
        except Utilisateur.DoesNotExist:
            messages.error(request, "Identifiants invalides")
            return redirect('connexion')
    return render(request,'sgeda/connexion/connexion.html')


def detail_reunion_frt(request,id):
    # get the list of all the reunions
    reunion = Reunion.objects.get(id=id)
    # get the list of salle from the reunion
    salle = Salle.objects.filter(reunion=reunion).get()
    # get the list of participants from the reunion
    # get the list of organisateur from the reunion
    organisateur = Utilisateur.objects.filter(id=reunion.organisateur.id).get()
    
    return render(request,'sgeda/detail_reunion_frt/detail_reunion_frt.html',{'reunion':reunion, 'salle':salle, 'organisateur':organisateur})

def mes_taches(request):
    # get the list of all the actions
    actions = Action.objects.filter(id_Utilisateur=request.user).order_by('-date_limite')
    paginator = Paginator(actions, 10)  # Show 10 actions per page
    page_number = request.GET.get('page')
    actions = paginator.get_page(page_number)
    return render(request,'sgeda/mes_taches/mes_taches.html',{'actions':actions})

def creer_compte(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        fonction = request.POST['fonction']
        departement = request.POST['departement']
        mot_de_passe = request.POST['password']
        utilisateur = Utilisateur(nom=nom, prenom=prenom, email=email, fonction=fonction, departement=departement, mot_de_passe=mot_de_passe)
        utilisateur.save()
        messages.success(request, "Compte créé avec succès!")
        return redirect('home')
    return render(request,'sgeda/creer_compte/creer_compte.html')

def deconnexion(request):
    logout(request)
    # Logique de déconnexion
    # Par exemple, vous pouvez utiliser request.session.flush() pour supprimer la session
    # ou rediriger vers une page de connexion
    messages.success(request, "Déconnexion réussie!")
    return redirect('connexion')

def page_reunion(request):

    reunions=Reunion.objects.all()
    paginator = Paginator(reunions, 3)  # Show 10 objects per page
    page_number = request.GET.get('page')
    reunions = paginator.get_page(page_number)
    return render(request,'sgeda/reunions/reunions.html',{'reunions':reunions})


def detail_reunion(request,id):
    # get the list of all the reunions
    reunions=Reunion.objects.get(id=id)
    paginator = Paginator(reunions, 3)  # Show 5 posts per page

    page_number = request.GET.get('page')  # Get current page number from URL
    reunions = paginator.get_page(page_number)
    return render(request,'sgeda/detail_reunion/detail_reunion.html',{'reunions':reunions})


def detail_formation(request,id):
    # get the list of all the formations
    formation=Formation.objects.get(id=id)
    nbr_participant=SInscrire.objects.filter(id=formation).count()
    return render(request,'sgeda/detail_formation/detail_formation.html',{'formation':formation,'nbr_participant':nbr_participant})
def formations(request):
    formations=Formation.objects.all()
    paginator = Paginator(formations, 3)  # Show 5 posts per page

    page_number = request.GET.get('page')  # Get current page number from URL
    formations = paginator.get_page(page_number)

    
    return render(request, 'sgeda/formations/formations.html',{'formations':formations})



@csrf_exempt
@require_POST
def search_reunions(request):
    try:
        data = json.loads(request.body)
        
        # Filtrage de base
        reunions = Reunion.objects.all()
        

        # Application des filtres
        if data.get('type'):
            reunions = reunions.filter(type=data['type'])
        
            
        # Sérialisation
        results = []
        for reunion in reunions:

            if reunion.image and hasattr(reunion.image, 'url'):
                image_url = request.build_absolute_uri(reunion.image.url)
            elif isinstance(reunion.image, str) and reunion.image.startswith(('http://', 'https://')):
                image_url = unquote(reunion.image)  # Décodage de l'URL
            else:
                image_url = None
    
            results.append({
                'id': reunion.id,
                'titre': reunion.titre,
                'type': reunion.type,
                'date_de_debut': reunion.date_de_debut.isoformat(),
                'salle': reunion.salle.nom if reunion.salle else None,
                'image': image_url,
                # Ajoutez d'autres champs selon votre modèle
            })
        
        return JsonResponse(results, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_POST
def search_formations(request):
    try:
        # Récupérer les paramètres de filtrage
        categorie = request.POST.get('categorie')
        
        statut = request.POST.get('statut')
        format_formation = request.POST.get('format')
        print("{}-{}-{}".format(categorie,statut,format_formation))
        # Filtrer les formations
        formations = Formation.objects.all()
        if categorie:
            formations = formations.filter(categorie=categorie)
            
        if statut:
            formations = formations.filter(statut=statut)
           
        if format_formation:
            formations = formations.filter(Modalite=format_formation)
            
        # Sérialiser les résultats
        data = []
        for formation in formations:
            data.append({
                'id': formation.id,
                'intitule': formation.intitule,
                'description': formation.description,
                'image': formation.image.url if formation.image else '',
                'categorie': formation.categorie,
                'statut': formation.statut,
                'date_de_debut': formation.date_de_debut.isoformat(),
                'duree': formation.duree,
                'format': formation.Modalite
            })
    
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def inscription(request):
    return render(request, 'sgeda/inscription/inscription.html')

def rediger_pv(request):
    return render(request,'administration/pages/rédigerPv.html')
def administration(request):
    # get the list of all the formations

    # Replace with your queryset
    reunions= Reunion.objects.all().order_by('date_de_debut')[:5]  # Show 10 objects per page
    formations= Formation.objects.all().order_by('date_de_debut')[:5]
    return render(request, 'administration/pages/index.html',{'formations':formations,'reunions':reunions})

def editer_formation(request, id):
    

    STATUT_CHOICES1 = [
        ('en attente', 'En attente'),
        ('ouvert', 'Ouvert'),
        ('fermé', 'Fermé'),
        ('en cours', 'Encours'),
    ]

    STATUT_CHOICES = [
        ('en présentiel', 'En présentiel'),
        ('à distance', 'A distance'),
    ]
    formation = Formation.objects.get(id=id)
    if request.method == 'POST':
        formation.intitule = request.POST['intitule']
        formation.prerequis = request.POST['prerequis']
        formation.duree = request.POST['duree']
        formation.objectif = request.POST['objectif']
        formation.public_cible = request.POST['public_cible']
        formation.programme = request.POST['programme']
        formation.statut = request.POST['statut']
        formation.Modalite = request.POST['modalite']
        formation.description = request.POST['description']
        formation.date_de_debut = request.POST['debut']
        formation.date_de_fin = request.POST['fin']
        formation.save()
        messages.success(request, "Formation enregistrée avec succès!")
        return redirect('editer', id=formation.id)
    
    formation.date_de_debut=formation.date_de_debut.strftime('%Y-%m-%d')
    formation.date_de_fin=formation.date_de_fin.strftime('%Y-%m-%d')  
     
    return render(request, 'administration/pages/editer_formation.html', {'formation':formation, 'STATUT_CHOICES': STATUT_CHOICES, 'STATUT_CHOICES1': STATUT_CHOICES1})


def supprimer(request, id):
    formation = Formation.objects.get(id=id)
    if request.method == 'POST':
        formation.delete()
        return redirect('administration')






def suivreDecision(request):
    # This view is for the decision tracking page
    # You can add logic here to fetch and display the necessary data
    #get all the decisions from the database and their initiateur,reunion and action
    decisions = Decision.objects.all().order_by('-date_prise')
      # Return the page object

    actions = Action.objects.all().order_by('-date_limite')
    return render(request, 'administration/pages/suivreDecision.html',{'decisions':decisions,'actions':actions})

def profil_util(request):
    return render(request, 'administration/pages/profil_utilisateur.html')


def editer_profil(request):
    if request.method=='POST':
        mot_de_passe=request.POST['password']
        nouveau_mot_de_passe=request.POST['password_confirm']

        nouveau_utilisateur=Utilisateur.objects.filter(id=request.user.id).get()
        if mot_de_passe==nouveau_mot_de_passe:

            nouveau_utilisateur.nom=request.POST['nom']
            nouveau_utilisateur.prenom=request.POST['prenom']
            nouveau_utilisateur.email=request.POST['email']
            nouveau_utilisateur.fonction=request.POST['fonction']
            nouveau_utilisateur.departement=request.POST['departement']
            nouveau_utilisateur.mot_de_passe=request.POST['password']
            nouveau_utilisateur.save()
            messages.success(request,"Enregistrement réussi avec succès")
            return redirect('profil_util')
        
        else:
            messages.error(request,"les deux mots de passe ne correspondent pas")
            return redirect('editer_profil')

    return render(request,'administration/pages/editer_profil.html')

def afficher_profil(request, id):
    utilisateur = Utilisateur.objects.get(id=id)
    return render(request, 'administration/pages/afficher_profil.html', {'utilisateur':utilisateur})

def afficher_reunion(request, id):
    reunion = Reunion.objects.get(id=id)
    # get the list of salle from the reunion
    salle=Salle.objects.filter(reunion=reunion).get()
    return render(request, 'administration/pages/afficher_reunion.html', {'reunion':reunion, 'salle':salle})

def editer_reunion(request, id):

    STATUT_CHOICES4 = [
        ('comité', 'Comité'),
        ('projet', 'Projet'),
        ('interne', 'interne'),
    ]
    

    salles=Salle.objects.all()
    reunion = Reunion.objects.get(id=id)
    if request.method == 'POST' and request.FILES.get('ordre-jour'):
        ordre_du_jour = request.FILES.get('ordre-jour')

        if ordre_du_jour.name.endswith('.pdf'):
            reunion.titre = request.POST['titre']
            reunion.type=request.POST['type']
            reunion.salle=Salle.objects.filter(numero=request.POST['salle']).get()
            ordre_du_jour = request.FILES.get('ordre-jour')
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'media/pdf'))
            filename = fs.save(ordre_du_jour.name, ordre_du_jour) 
            file_url = os.path.join('media/pdf', filename)
            reunion.date_de_debut=datetime.strptime(request.POST['debut'], '%Y-%m-%d').date()
            reunion.date_de_fin=datetime.strptime(request.POST['fin'], '%Y-%m-%d').date()
            reunion.ordre_du_jour=file_url
            reunion.organisateur=request.user
            reunion.save()
            messages.success(request, "Les modifications sont enregistrées avec succès")
            return redirect('editer_reunion', id=reunion.id)
    
    return render(request, 'administration/pages/editer_reunion.html', {'reunion':reunion,'salles':salles,'STATUT_CHOICES4':STATUT_CHOICES4})

def supprimer_reunion(request, id):
    reunion = Reunion.objects.get(id=id)
    if request.method == 'POST':
        reunion.delete()
        return redirect('administration')
    

def afficher(request, id):
    formation = Formation.objects.get(id=id)
    return render(request, 'administration/pages/afficher.html', {'formation':formation})

def planifierEvent(request):
 
    return render(request, 'administration/pages/planifier_evenement.html')
    

def reporting(request):

    nombre_reunion=Reunion.objects.all().count()
    nombre_formation=Formation.objects.all().count()
    nombre_action=Action.objects.all().count()
    nombre_decision=Decision.objects.all().count()
    reunions=Reunion.objects.all()
    actions=Action.objects.all()
    decisions=Decision.objects.all()
    formations=Formation.objects.all()
    return render(request,'administration/pages/afficher_reporting.html',{'formations':formations,'nombre_reunion':nombre_reunion,'nombre_formation':nombre_formation,'nombre_decision':nombre_decision,'nombre_action':nombre_action,'reunions':reunions,'actions':actions,'decisions':decisions})

def afficher_decision(request, id):
    decision = Decision.objects.get(id=id)
    # get the list of action from the decision
    actions = Action.objects.filter(id_decision=id).order_by('-date_limite')
    return render(request, 'administration/pages/afficher_decision.html', {'decision':decision, 'actions':actions})

def afficher_formations_reunions(request):
    formations=Formation.objects.all()

    reunions=Reunion.objects.all()
    paginator = Paginator(formations, 3)  # Show 10 formations per page    
    page_number = request.GET.get('page')
    formations = paginator.get_page(page_number)
    paginator = Paginator(reunions, 3)  # Show 10 reunions per page    
    page_number = request.GET.get('page')
    reunions = paginator.get_page(page_number)
    return render(request,'administration/pages/afficher_formations_reunions.html', {'formations': formations, 'reunions': reunions})

def afficher_actions_decisions(request):
    # get the list of actions from the decision
    actions = Action.objects.all().order_by('-date_limite')
    paginator = Paginator(actions,3)  # Show 10 actions per page
    page_number = request.GET.get('page')
    actions = paginator.get_page(page_number)

    decisions= Decision.objects.all().order_by('-date_prise')
    paginator = Paginator(decisions, 3)  # Show 10 decisions per page
    page_number = request.GET.get('page')
    decisions = paginator.get_page(page_number)
    return render(request, 'administration/pages/afficher_actions_decisions.html', {'actions': actions,'decisions': decisions})

def afficher_action(request,id):
    action=Action.objects.get(id=id)
    return render(request,'administration/pages/afficher_action.html',{'action':action})

def televerserSupports(request):
    if request.method == 'POST':
        # Initialisation du modèle
        support = SupportDeCours()
        support.intitule = request.POST.get('titre', '')
        support.description = request.POST.get('description', '')
        support.siteweb = request.POST.get('lien', '') if request.POST.get('lien') else None

        # Gestion des fichiers uploadés
        fichier_pdf = request.FILES.get('fichier_document')
        fichier_video = request.FILES.get('fichier_video')

        # Configuration du stockage
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'supports_cours'))

        try:
            # Traitement du fichier PDF/DOCX/PPT
            if fichier_pdf:
                ext = os.path.splitext(fichier_pdf.name)[1].lower()
                if ext in ['.pdf', '.docx', '.ppt', '.pptx']:
                    filename = fs.save(f"documents/{fichier_pdf.name}", fichier_pdf)
                    support.fichierpdf = os.path.join('supports_cours', filename)
                else:
                    messages.error(request, "Format de document non supporté. Utilisez PDF, DOCX ou PPT.")
                    return redirect('televerserSupports')

            # Traitement du fichier vidéo
            if fichier_video:
                ext = os.path.splitext(fichier_video.name)[1].lower()
                if ext in ['.mp4', '.avi', '.mov']:
                    filename = fs.save(f"videos/{fichier_video.name}", fichier_video)
                    support.fichiervideo = os.path.join('supports_cours', filename)
                else:
                    messages.error(request, "Format vidéo non supporté. Utilisez MP4, AVI ou MOV.")
                    return redirect('televerserSupports')

            # Vérification qu'au moins un support est fourni
            if not any([support.fichierpdf, support.fichiervideo, support.lien_web]):
                messages.error(request, "Vous devez fournir au moins un support (document, vidéo ou lien)")
                return redirect('televerserSupports')

            # Sauvegarde en base de données
            support.save()
            messages.success(request, "Support de cours enregistré avec succès!")
            return redirect('televerserSupports')

        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {str(e)}")
            return redirect('televerserSupports')
    return render(request,"administration/pages/televerserSupports.html")

def planifier_formation(request):
    salles=Salle.objects.all()
    STATUT_CHOICES3 = [
        ('En présentiel', 'En présentiel'),
        ('En ligne', 'En ligne'),
    ]

    STATUT_CHOICES2 = [
        ('Ouvert', 'Ouvert'),
        ('Fermé', 'Fermé'),
        ('En cours', 'En cours'),
        ('En attente', 'En attente'),
    ]

    if request.method == 'POST' :
        #Planifier une formation d'abord et enregistrer la salle dans alquelle va se derouler la formation
        formation = Formation()
        formation.intitule = request.POST['intitule']
        formation.description = request.POST['description']
        formation.prerequis = request.POST['prerequis']
        formation.duree = request.POST['duree']
        formation.objectif = request.POST['objectif']
        formation.public_cible = request.POST['public_cible']
        formation.programme = request.POST['programme']
        formation.statut = request.POST['statut']
        formation.Modalite = request.POST['modalite']
        formation.date_de_debut = request.POST['debut']
        formation.date_de_fin = request.POST['fin']
        formation.id_Utilisateur = Utilisateur.objects.get(id=request.POST['id_Utilisateur'])
        formation.salle=Salle.objects.get(numero=request.POST['salle'])
        formation.save()

        messages.success(request, "Enregistrement réusiie")

        return redirect('planifier_formation')
    return render(request,'administration/pages/planifier_formation.html',{'STATUT_CHOICES3':STATUT_CHOICES3,'STATUT_CHOICES2':STATUT_CHOICES2,'salles':salles})

def planifier_reunion(request):
    salles=Salle.objects.all()
    Utilisateurs = Utilisateur.objects.all()
    STATUT_CHOICES4 = [
        ('comité', 'Comité'),
        ('projet', 'Projet'),
        ('interne', 'interne'),
    ]
    if request.method=='POST' and request.FILES.get('ordre-jour'):
        ordre_du_jour = request.FILES['ordre-jour']

        if ordre_du_jour.name.endswith('.pdf'):
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'media/pdf'))  # or os.path.join(...)
            filename = fs.save(ordre_du_jour.name, ordre_du_jour) 
            file_url = os.path.join('media/pdf', filename)
            reunion= Reunion()
            reunion.titre=request.POST['titre']
            reunion.type=request.POST['type']
            reunion.ordre_du_jour=file_url
            reunion.salle=Salle.objects.get(numero=request.POST['salle'])
            reunion.organisateur=request.user
            date_de_debut=request.POST['debut-reunion']
            
            reunion.date_de_debut=datetime.strptime(date_de_debut, '%Y-%m-%d').date()
            reunion.date_de_fin=datetime.strptime(request.POST['fin-reunion'], '%Y-%m-%d').date()
            reunion.save()

            messages.success(request, "Enregistrement réusiie")

            return redirect('planifier_reunion')
        
        else:
            messages.error(request,'Vous devez soumettre un fichier pdf')
    return render(request,'administration/pages/planifier_reunion.html',{'STATUT_CHOICES4':STATUT_CHOICES4,'salles':salles,'utilisateurs':Utilisateurs})

def planifier_action(request):
    decisions= Decision.objects.all()
    
    Utilisateurs = Utilisateur.objects.all()
    STATUT_CHOICES1 = [
        ('en attente', 'En attente'),
        ('en cours', 'En cours'),
        ('exécuter', 'Exécuter'),
    ]
    if request.method=='POST':
        action = Action()
        action.titre= request.POST['titre']
        
        #convertis la en format %Y-%m-%d
        action.date_limite = datetime.strptime(request.POST['deadline'], '%Y-%m-%d').date()
        action.description = request.POST['description']
        action.commentaire= request.POST['commentaire']
        action.progression = request.POST['statut']
        action.id_Utilisateur = request.user
        action.id_decision = Decision.objects.get(id=request.POST['decision'])
        action.save()

        #assigner l'action a un utilisateur

        assigner = AssignerA()
        assigner.id_Utilisateur = Utilisateur.objects.get(id=request.POST['executeur'])
        assigner.id = action
        assigner.save()
        messages.success(request, "Enregistrement réusiie")

        return redirect('planifier_action')

    return render(request,'administration/pages/planifier_action.html',{'STATUT_CHOICES1':STATUT_CHOICES1,'decisions':decisions,'utilisateurs':Utilisateurs})

def planifier_decision(request):
    reunions= Reunion.objects.all()
    if request.method=='POST':
            #Planifier une decision d'abord et enregistrer la réunion concernée 
            decision = Decision()
            decision.titre= request.POST['titre']
            decision.description = request.POST['description-decision']
            decision.id_Utilisateur =request.user
            decision.id_Reunion = Reunion.objects.get(id=request.POST['reunion'])
            decision.save()
            messages.success(request, "Enregistrement réusiie")
            return redirect('planifier_evenement')
    
    return render(request,'administration/pages/planifier_decision.html',{'reunions':reunions})