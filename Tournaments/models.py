from django.db import models
from users.models import User

from django.core.exceptions import ValidationError


class Game(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='game_images/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.name
# Create your models here.

class CustomImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', 150)
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        # Check if value is provided; if not, return without any validation
        if value is None:
            return super().clean(value, model_instance)

        # Ensure value is an instance of UploadedFile to access the file attribute
        if hasattr(value, 'name'):
            file_name = value.name  # Use value.name instead of self.file.name
            if len(file_name) > self.max_length:
                raise ValidationError(
                    f'Ensure this filename has at most {self.max_length} characters (it has {len(file_name)}).'
                )

        return super().clean(value, model_instance)

class Tournament(models.Model):
    tournament_name = models.CharField(max_length=255)
    email_address = models.EmailField()
    contact_number = models.CharField(max_length=15)

    # New fields for event details
    event_date = models.DateField()  # The date when the event will occur
    event_start_time = models.TimeField()  # The start time of the event
    last_registration_date = models.DateField()  # Last date for participants to register

    tournament_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Optional
    banner_image = CustomImageField(upload_to='tournament_banners/', blank=True, null=True)  # Optional

    # Foreign key to the Game model
    venue = models.CharField(max_length=255, blank=True, null=True)  # Optional venue for the tournament
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='tournaments')
    is_draft = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tournaments', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.tournament_name
class Deck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')  # Foreign key to User
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='decks')
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='decks/')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards', null=True, blank=True)
    # name = models.CharField(max_length=255, null=True, blank=True)
    # description = models.TextField(blank=True, null=True)
    # image = models.ImageField(upload_to='cards/', blank=True, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    card_type = models.CharField(max_length=50, null=True, blank=True)
    power = models.CharField(max_length=50, null=True, blank=True)
    effect = models.CharField(max_length=255, null=True, blank=True)
    images_url = models.URLField(blank=True, null=True)
    card_id = models.CharField(max_length=50, null=True, blank=True)  # You can adjust the max_length as needed
    card_quantity = models.CharField(max_length=50,null=True, blank=True)

    def __str__(self):
        return f"{self.name or 'Unnamed Card'} - {self.title or 'No Title'}"
class Participant(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='participants', null=True, blank=True)  # Foreign key to Deck
    registration_date = models.DateField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    total_score = models.IntegerField(default=0)
    is_disqualified = models.BooleanField(default=False)
    arrived_at_venue = models.BooleanField(default=False)
    is_ready=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.tournament.tournament_name} ({self.payment_status})"

class MatchScore(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    rank = models.IntegerField(null=True, blank=True)  # Rank of the participant in the match
    round = models.IntegerField(null=True, blank=True)  # Round number in the tournament
    win = models.BooleanField(default=False)  # If the participant won the match
    lose = models.BooleanField(default=False)  # If the participant lost the match
    score = models.IntegerField(default=0)  # Score of the participant

    def __str__(self):
        return f"{self.participant.user.username} - {self.tournament.tournament_name} ({self.score} points)"

class FeaturedTournament(models.Model):
    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name='featured_tournament')
    is_featured = models.BooleanField(default=False)
    featured_date = models.DateField()

    def __str__(self):
        return f"Featured Tournament: {self.tournament.tournament_name} (Featured on {self.featured_date})"


class BannerImage(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='banner_images')
    image = models.ImageField(upload_to='tournament_banners/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Banner for {self.tournament.tournament_name} (Uploaded on {self.uploaded_at})"
class Fixture(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    participant1 = models.ForeignKey(Participant, related_name='fixture_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(Participant, related_name='fixture_participant2', on_delete=models.CASCADE,null=True, blank=True,)
    round_number = models.IntegerField()
    match_date = models.DateTimeField()
    start_time=models.BooleanField(default=False)


    nominated_winner = models.ForeignKey(Participant, null=True, blank=True, related_name='nominated_fixtures', on_delete=models.SET_NULL)
    verified_winner = models.ForeignKey(Participant, null=True, blank=True, related_name='verified_fixtures', on_delete=models.SET_NULL)
    is_verified = models.BooleanField(default=False)
    is_tournament_completed=models.BooleanField(default=False)

    def __str__(self):
        # Assuming `Participant` has a `user` field linked to `User` model
        participant1_username = self.participant1.user.username if self.participant1 and hasattr(self.participant1, 'user') else "No Participant"

        if self.participant2:
            participant2_username = self.participant2.user.username if hasattr(self.participant2, 'user') else "No Participant"
            return f"{self.tournament.tournament_name} - Round {self.round_number}: {participant1_username} vs {participant2_username}"
        else:
            return f"{self.tournament.tournament_name} - Round {self.round_number}: {participant1_username} has a bye"