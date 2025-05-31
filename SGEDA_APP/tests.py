from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime  import timedelta
from .test_utils import get_next_salle_numero
from .models import (
    Utilisateur, Salle, Formation, ProcesRendu, Reunion, 
    Organiser, SupportDeCours, Decision, Action,
    AssignerA, SInscrire, Assister, Utiliser
)


class UtilisateurModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'nom': 'Doe',
            'prenom': 'John',
            'mot_de_passe': 'password123',
            'role': 'Manager',
            'fonction': 'Directeur',
            'departement': 'IT',
            'is_staff': True
        }
        self.user = Utilisateur.objects.create_user(**self.user_data)
        self.superuser = Utilisateur.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            nom='Admin',
            prenom='Super',
            role='Admin',
            fonction='Administrateur',
            departement='Management'
        )

    def test_create_user(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.nom, 'Doe')
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_staff)  # Car is_staff=True dans setUp

    def test_create_superuser(self):
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.is_staff)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'Doe')

    def test_photo_de_profil_upload(self):
        photo = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        user = Utilisateur.objects.create_user(
            email='photo@test.com',
            nom='Photo',
            prenom='Test',
            mot_de_passe='pass123',
            role='Test',
            fonction='Test',
            departement='Test',
            photo_de_profil=photo
        )
        self.assertTrue(user.photo_de_profil.name.startswith('media/photo/'))

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            Utilisateur.objects.create_user(email='')
            
    def tearDown(self):
        # Nettoie tous les utilisateurs créés
        Utilisateur.objects.all().delete()

class SalleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crée des données partagées entre tous les tests de la classe
        
        
        cls.salle = Salle.objects.create(
            numero=get_next_salle_numero(),
            nom='Salle A'
        )
    def test_salle_creation(self):
        self.assertEqual(self.salle.numero, self.salle.numero)
        self.assertEqual(self.salle.nom, 'Salle A')

    def test_salle_str(self):
        self.assertEqual(str(self.salle), f'Salle A (n°{self.salle.numero})')

class FormationModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            email=get_unique_email("formateur"),
            nom='Formateur',
            prenom='Test',
            mot_de_passe='password123',
            role='Formateur',
            fonction='Enseignant',
            departement='Education'
        )
        
        self.salle = Salle.objects.create(numero=get_next_salle_numero(), nom='Amphi B')
        
        start_date =timezone.now() + timedelta(days=7)
        end_date = start_date + timedelta(hours=2)
        
        self.formation = Formation.objects.create(
            intitule='Formation Django',
            description='Apprendre Django',
            prerequis='Python de base',
            duree='2 heures',
            categorie='informatique',
            Modalite='en présentiel',
            objectif='Maîtriser Django',
            public_cible='Développeurs',
            date_de_debut=start_date,
            date_de_fin=end_date,
            programme='Programme détaillé',
            statut='ouvert',
            id_Utilisateur=self.user,
            salle=self.salle,
            intervenant=self.user
        )

    def test_formation_creation(self):
        self.assertEqual(self.formation.intitule, 'Formation Django')
        self.assertEqual(self.formation.categorie, 'informatique')
        self.assertEqual(self.formation.Modalite, 'en présentiel')
        self.assertFalse(self.formation.archive)

    def test_formation_str(self):
        self.assertEqual(str(self.formation), 'Formation Django')

    
    def test_formation_foreign_keys(self):
        self.assertEqual(self.formation.id_Utilisateur, self.user)
        self.assertEqual(self.formation.salle, self.salle)
        self.assertEqual(self.formation.intervenant, self.user)



def get_unique_email(prefix):
    """Génère un email unique basé sur un préfixe et le timestamp"""
    return f"{prefix}_{timezone.now().strftime('%Y%m%d%H%M%S%f')}@example.com"

class ReunionModelTest(TestCase):
    def setUp(self):
        # Crée un utilisateur avec email unique
        self.user = Utilisateur.objects.create_user(
            email=get_unique_email("organisateur"),
            nom='Organisateur',
            prenom='Test',
            mot_de_passe='password123',
            role='Organisateur',
            fonction='Manager',
            departement='Management'
        )
        
        # Crée une salle avec numéro unique
 
        
        self.salle = Salle.objects.create(
            numero=get_next_salle_numero(),
            nom='Salle C'
        )
        
        # Crée la réunion
        self.reunion = Reunion.objects.create(
            titre='Réunion stratégique',
            type='comité',
            ordre_du_jour=SimpleUploadedFile("ordre.pdf", b"file_content"),
            date_de_debut=timezone.now() ,
            date_de_fin=timezone.now() + timedelta(days=1),
            organisateur=self.user,
            salle=self.salle
        )

class ProcesRenduModelTest(TestCase):
    def setUp(self):
        self.redacteur = Utilisateur.objects.create_user(
            email=get_unique_email("redacteur"),
            nom='Redacteur',
            prenom='Test',
            mot_de_passe='password123',
            role='Rédacteur',
            fonction='Secrétaire',
            departement='Administration'
        )
        
        self.validateur = Utilisateur.objects.create_user(
            email=get_unique_email("validateur"),
            nom='Validateur',
            prenom='Test',
            mot_de_passe='password123',
            role='Validateur',
            fonction='Manager',
            departement='Management'
        )
        
        self.proces = ProcesRendu.objects.create(
            proces_verbal='PV123',
            compte_rendu='CR123',
            redacteur=self.redacteur,
            validateur=self.validateur
        )

    def test_proces_rendu_creation(self):
        self.assertEqual(self.proces.proces_verbal, 'PV123')
        self.assertEqual(self.proces.compte_rendu, 'CR123')
        self.assertFalse(self.proces.archive)

    def test_proces_rendu_str(self):
        self.assertEqual(str(self.proces), f'Proces-{self.proces.id}')

class SupportDeCoursModelTest(TestCase):
    def setUp(self):
        # Génère un email unique
        unique_email = f"support_{timezone.now().timestamp()}@example.com"
        
        self.user = Utilisateur.objects.create_user(
            email=unique_email,
            nom='Support',
            prenom='Test',
            mot_de_passe='password123',
            role='Enseignant',
            fonction='Formateur',
            departement='Education'
        )
        
        pdf_file = SimpleUploadedFile("cours.pdf", b"file_content", content_type="application/pdf")
        video_file = SimpleUploadedFile("video.mp4", b"file_content", content_type="video/mp4")
        
        self.support = SupportDeCours.objects.create(
            intitule='Support Django',
            fichierpdf=pdf_file,
            video=video_file,
            siteweb='https://example.com',
            description='Support de cours sur Django',
            id_Utilisateur=self.user
        )

    def test_support_creation(self):
        self.assertEqual(self.support.intitule, 'Support Django')
        self.assertTrue(self.support.fichierpdf.name.startswith('media/pdf/'))
        self.assertTrue(self.support.video.name.startswith('media/videos/'))
        self.assertEqual(self.support.siteweb, 'https://example.com')

    def test_support_str(self):
        self.assertEqual(str(self.support), f'Support-{self.support.id}')

class DecisionModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            email=get_unique_email("decideur"),
            nom='Decideur',
            prenom='Test',
            mot_de_passe='password123',
            role='Manager',
            fonction='Directeur',
            departement='Management'
        )
        
        self.salle = Salle.objects.create(numero=get_next_salle_numero(), nom='Salle D')
        
        start_date =timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(hours=1)
        
        self.reunion = Reunion.objects.create(
            titre='Réunion décisionnelle',
            type='comité',
            ordre_du_jour=SimpleUploadedFile("ordre.pdf", b"file_content"),
            date_de_debut=start_date,
            date_de_fin=end_date,
            organisateur=self.user,
            salle=self.salle
        )
        
        self.decision = Decision.objects.create(
            titre='Nouvelle stratégie',
            description='Description de la décision',
            id_Utilisateur=self.user,
            id_Reunion=self.reunion
        )

    def test_decision_creation(self):
        self.assertEqual(self.decision.titre, 'Nouvelle stratégie')
        self.assertEqual(self.decision.description, 'Description de la décision')
        self.assertFalse(self.decision.archive)
        self.assertEqual(self.decision.id_Utilisateur, self.user)
        self.assertEqual(self.decision.id_Reunion, self.reunion)

    def test_decision_str(self):
        self.assertEqual(str(self.decision), f'Décision-{self.decision.id}')

class ActionModelTest(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            email=get_unique_email("action"),
            nom='Action',
            prenom='Test',
            mot_de_passe='password123',
            role='Responsable',
            fonction='Manager',
            departement='Operations'
        )
        
        # Création des dépendances
        reunion = Reunion.objects.create(
            titre='Réunion action',
            type='projet',
            ordre_du_jour=SimpleUploadedFile("ordre.pdf", b"file_content"),
            date_de_debut=timezone.now() ,
            date_de_fin=timezone.now() + timedelta(days=1),
            organisateur=self.user
        )
        
        decision = Decision.objects.create(
            titre='Décision action',
            description='Description',
            id_Utilisateur=self.user,
            id_Reunion=reunion
        )
        
        self.action = Action.objects.create(
            titre='Action 1',
            description='Description action',
            date_limite=timezone.now() + timedelta(days=7),
            commentaire='Commentaire',
            id_Utilisateur=self.user,
            id_decision=decision,
            progression='en attente'
        )

    def test_action_creation(self):
        self.assertEqual(self.action.titre, 'Action 1')
        self.assertEqual(self.action.progression, 'en attente')
        self.assertFalse(self.action.archive)

    def test_action_str(self):
        self.assertEqual(str(self.action), f'Action-{self.action.id}')

class RelationModelsTest(TestCase):
    def setUp(self):
        # Création des utilisateurs avec des emails uniques
        self.user1 = Utilisateur.objects.create_user(
            email=f"user1_{timezone.now().timestamp()}@test.com",
            nom='User1',
            prenom='Test',
            mot_de_passe='password123',
            role='Membre',
            fonction='Employé',
            departement='IT'
        )
        
        self.user2 = Utilisateur.objects.create_user(
            email=f"user2_{timezone.now().timestamp()}@test.com",
            nom='User2',
            prenom='Test',
            mot_de_passe='password123',
            role='Membre',
            fonction='Employé',
            departement='HR'
        )
        # ... reste du code
        # Création d'une salle
        self.salle = Salle.objects.create(numero=get_next_salle_numero(), nom='Salle E')
        
        # Création d'une formation
        start_date = timezone.now() + timedelta(days=7)
        end_date = start_date + timedelta(hours=2)
        
        self.formation = Formation.objects.create(
            intitule='Formation relation',
            description='Description',
            prerequis='Aucun',
            duree='2 heures',
            categorie='informatique',
            Modalite='en présentiel',
            objectif='Objectif',
            public_cible='Public',
            date_de_debut=start_date,
            date_de_fin=end_date,
            programme='Programme',
            statut='ouvert',
            id_Utilisateur=self.user1,
            salle=self.salle,
            intervenant=self.user1
        )
        
        # Création d'une réunion
        self.reunion = Reunion.objects.create(
            titre='Réunion relation',
            type='interne',
            ordre_du_jour=SimpleUploadedFile("ordre.pdf", b"file_content"),
            date_de_debut=timezone.now(),
            date_de_fin=timezone.now() + timedelta(days=1),
            organisateur=self.user1
        )
        
        # Création d'un support de cours
        self.support = SupportDeCours.objects.create(
            intitule='Support relation',
            description='Description',
            id_Utilisateur=self.user1
        )
        
        # Création d'une décision
        decision = Decision.objects.create(
            titre='Décision relation',
            description='Description',
            id_Utilisateur=self.user1,
            id_Reunion=self.reunion
        )
        
        # Création d'une action
        self.action = Action.objects.create(
            titre='Action relation',
            description='Description',
            date_limite=timezone.now() + timedelta(days=7),
            commentaire='Commentaire',
            id_Utilisateur=self.user1,
            id_decision=decision,
            progression='en attente'
        )

    def test_organiser_relation(self):
        organiser = Organiser.objects.create(
            reunion=self.reunion,
            utilisateur=self.user2
        )
        self.assertEqual(organiser.reunion, self.reunion)
        self.assertEqual(organiser.utilisateur, self.user2)
        
        # Test de l'unicité
        with self.assertRaises(Exception):
            Organiser.objects.create(
                reunion=self.reunion,
                utilisateur=self.user2
            )

    def test_sinscrire_relation(self):
        inscription = SInscrire.objects.create(
            id=self.formation,
            id_Utilisateur=self.user2
        )
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib import messages
from unittest.mock import patch, MagicMock
from SGEDA_APP.views import connexion, deconnexion

class SimpleViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
    
    def test_connexion_view_get(self):
        response = self.client.get('/connexion/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sgeda/connexion/connexion.html')
    
    @patch('SGEDA_APP.views.login')
    @patch('SGEDA_APP.views.redirect')
    @patch('SGEDA_APP.views.Utilisateur.objects.get')
    def test_connexion_view_post_success(self, mock_get, mock_redirect, mock_login):
        # Configuration de la requête
        request = self.factory.post('/connexion/', {
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Configuration du système de messages
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)
        
        # Configuration des mocks
        mock_user = MagicMock()
        mock_get.return_value = mock_user
        
        # Mock de la réponse de redirection
        mock_response = MagicMock()
        mock_response.status_code = 302
        mock_redirect.return_value = mock_response
        
        response = connexion(request)
        
        # Vérifications
        mock_get.assert_called_once_with(email='test@example.com', mot_de_passe='password123')
        mock_login.assert_called_once_with(request, mock_user)
        self.assertEqual(response.status_code, 302)
    
    @patch('SGEDA_APP.views.logout')
    def test_deconnexion_view(self, mock_logout):
        request = self.factory.get('/deconnexion/')
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)
        
        # Mock de la réponse de redirection
        mock_response = MagicMock()
        mock_response.status_code = 302
        with patch('SGEDA_APP.views.redirect', return_value=mock_response):
            response = deconnexion(request)
        
        mock_logout.assert_called_once()
        self.assertEqual(response.status_code, 302)