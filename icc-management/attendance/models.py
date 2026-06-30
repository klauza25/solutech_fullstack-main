from django.db import models
from django.conf import settings # Permet de référencer ton CustomUser proprement

class ServiceEvent(models.Model):
    """Les différents cultes et réunions de l'église"""
    EVENT_TYPES = (
        ('culte_dimanche', 'Culte du Dimanche'),
        ('priere_mercredi', 'Prière du Mercredi'),
        ('veillee', 'Veillée'),
        ('reunion_dept', 'Réunion de Département'),
        ('autre', 'Autre'),
    )
    
    name = models.CharField("Nom de l'événement", max_length=200)
    event_type = models.CharField("Type", max_length=50, choices=EVENT_TYPES)
    date = models.DateField("Date")
    description = models.TextField("Description", blank=True, null=True)

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['-date'] # Les plus récents en premier

    def __str__(self):
        return f"{self.name} - {self.date}"

class Attendance(models.Model):
    """Le pointage de présence d'un serviteur à un événement"""
    STATUS_CHOICES = (
        ('present', 'Présent'),
        ('absent', 'Absent'),
        ('excused', 'Excusé'),
    )
    
    servant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="attendances", 
        verbose_name="Serviteur"
    )
    event = models.ForeignKey(
        ServiceEvent, 
        on_delete=models.CASCADE, 
        related_name="attendances", 
        verbose_name="Événement"
    )
    # On garde le département ici pour faciliter les filtres et les graphiques plus tard
    department = models.ForeignKey(
        'account.Department', 
        on_delete=models.CASCADE, 
        related_name="attendances", 
        verbose_name="Département"
    )
    status = models.CharField("Statut", max_length=20, choices=STATUS_CHOICES, default='present')
    
    # Pour savoir qui a fait le pointage (le chef de département)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="marked_attendances", 
        verbose_name="Pointé par"
    )
    timestamp = models.DateTimeField("Date de pointage", auto_now_add=True)

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        # RÈGLE D'OR : Un serviteur ne peut être pointé qu'une seule fois par événement
        unique_together = ('servant', 'event') 

    def __str__(self):
        return f"{self.servant} - {self.event} ({self.get_status_display()})"