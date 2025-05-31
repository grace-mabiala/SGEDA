
# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est requise")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    mot_de_passe = models.CharField(max_length=80)  # Note: Il est préférable d'utiliser le système de mot de passe intégré de Django
    email = models.EmailField(max_length=50, unique=True)
    role = models.CharField(max_length=80)
    fonction = models.CharField(max_length=80)
    departement = models.CharField(max_length=80)
    photo_de_profil = models.FileField(upload_to='media/photo/')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom','password','role','fonction','departement']

    def __str__(self):
        return self.nom

class Salle(models.Model):
    numero = models.SmallIntegerField(primary_key=True)
    nom = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.nom} (n°{self.numero})"

class Formation(models.Model):

    id = models.AutoField(primary_key=True)
    intitule = models.CharField(max_length=50)
    description = models.TextField()
    prerequis = models.TextField()
    duree = models.CharField(max_length=10)

    STATUT_CHOICES = [
        ('management', 'Management'),
        ('communication', 'Communication'),
        ('informatique', 'Informatique'),
        ('dévéloppement personnel', 'dévéloppement personnel'),
    ]
    categorie=models.CharField(max_length=80,choices=STATUT_CHOICES,default='Informatique')
    
    STATUT_CHOICES = [
        ('en présentiel', 'En présentiel'),
        ('en ligne', 'En ligne'),
    ]
    
    Modalite = models.CharField(max_length=20,choices=STATUT_CHOICES)
    
    objectif = models.CharField(max_length=100)
    public_cible = models.CharField(max_length=100)
    date_de_debut = models.DateTimeField()
    date_de_fin = models.DateTimeField()
    programme = models.TextField()
    STATUT_CHOICES1 = [
        ('en attente', 'En attente'),
        ('ouvert', 'Ouvert'),
        ('fermé', 'Fermé'),
        ('en cours', 'Encours'),
    ]
    statut = models.CharField(max_length=50,choices=STATUT_CHOICES1)
    image= models.FileField(upload_to='media/image_formations',default='https://images.unsplash.com/photo-1522202176988-66273c2fd55f')
    archive=models.BooleanField(default=False)

    id_Utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,)
    salle= models.ForeignKey(Salle, on_delete=models.CASCADE, null=True, blank=True)
    intervenant= models.ForeignKey(Utilisateur, on_delete=models.CASCADE,default=1,related_name='intervenant')

    def __str__(self):
        return self.intitule



class ProcesRendu(models.Model):
    id = models.AutoField(primary_key=True)
    proces_verbal = models.CharField(max_length=100)
    compte_rendu = models.CharField(max_length=100)
    archive=models.BooleanField(default=False)
    redacteur= models.ForeignKey(Utilisateur, on_delete=models.CASCADE,default=1,related_name='redacteur')
    validateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,default=1,related_name='validateur')
    
    def __str__(self):
        return f"Proces-{self.id}"
    



class Reunion(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=60)
    STATUT_CHOICES2 = [
        ('comité', 'Comité'),
        ('projet', 'Projet'),
        ('interne', 'interne'),
    ]
    type = models.CharField(choices=STATUT_CHOICES2, max_length=20)
    ordre_du_jour = models.FileField(upload_to='media/pdf/')
    date_de_debut = models.DateTimeField()
    date_de_fin = models.DateTimeField()
    image= models.FileField(upload_to='media/image_reunions',default='https://images.unsplash.com/photo-1522202176988-66273c2fd55f')
    archive=models.BooleanField(default=False)
    organisateur= models.ForeignKey(Utilisateur, on_delete=models.CASCADE, default=1)
    salle= models.ForeignKey(Salle, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.titre
  
class Organiser(models.Model):
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("reunion", "utilisateur")

class SupportDeCours(models.Model):
    id = models.AutoField(primary_key=True)
    intitule=models.CharField(max_length=60,default="Décision")
    fichierpdf = models.FileField(upload_to='media/pdf/',null=True,blank=True)
    video = models.FileField(upload_to='media/videos/',null=True,blank=True)
    siteweb = models.URLField(max_length=200,null=True,blank=True)

    description=models.TextField(default='Déscription du support facultatif')
    id_Utilisateur = models.ForeignKey(Utilisateur, default=1,on_delete=models.CASCADE)
    def __str__(self):
        return f"Support-{self.id}"

class Decision(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=60,default="Décision")
    description = models.TextField()
    date_prise = models.DateField(auto_now=True)
    archive=models.BooleanField(default=False)
    id_Utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    id_Reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE)
    def __str__(self):
        return f"Décision-{self.id}"

class Action(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=15,default="action")
    description = models.TextField()
    date_limite = models.DateTimeField()
    commentaire = models.TextField()
    archive=models.BooleanField(default=False)
    id_Utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    id_decision = models.ForeignKey(Decision, on_delete=models.CASCADE)
   
    STATUT_CHOICES = [
        ('en attente', 'En attente'),
        ('en cours', 'En cours'),
        ('exécuté', 'Exécuté'),
    ]
    progression = models.CharField(max_length=15, choices=STATUT_CHOICES)

    def __str__(self):
        return f"Action-{self.id}"

class AssignerA(models.Model):
    id = models.ForeignKey(Action, on_delete=models.CASCADE, primary_key=True)
    id_Utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('id', 'id_Utilisateur'),)
    
    def __str__(self):
        return f"Assignation-{self.id}-{self.id_Utilisateur}"

class SInscrire(models.Model):
    id = models.ForeignKey(Formation, on_delete=models.CASCADE, primary_key=True)
    id_Utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_d_inscription = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (('id', 'id_Utilisateur'),)
    
    def __str__(self):
        return f"Inscription-{self.id}-{self.id_Utilisateur}"

    
class Assister(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE)
    heure_participation = models.TimeField()
    
    STATUT_CHOICES = [
        ('present', 'Présent'),
        ('absent', 'Absent'),
    ]
    statut = models.CharField(max_length=7, choices=STATUT_CHOICES)

    class Meta:
        unique_together = (('utilisateur', 'reunion'),)

class Utiliser(models.Model):
    id = models.ForeignKey(SupportDeCours, on_delete=models.CASCADE, primary_key=True)
    id_formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('id', 'id_formation'),)
    
    def __str__(self):
        return f"Utilisation-{self.id}-{self.id_formation}"
    

