# serializers.py
from rest_framework import serializers
from .models import *
from users.serializers import UserProfileSerializer

from rest_framework import serializers
from .models import Tournament, Game,Deck,Participant,Fixture,MatchScore
from users.models import User
from rest_framework import serializers
from .models import Tournament, Participant, MatchScore





class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
class TournamentSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(write_only=True)  # Field for passing the game name
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # User creating the tournament

    class Meta:
        model = Tournament
        fields = [
            'id','tournament_name', 'email_address', 'contact_number',
            'event_date', 'event_start_time', 'last_registration_date',
            'tournament_fee', 'banner_image', 'venue','game_name', 'is_draft', 'created_by','created_at','featured','is_active',
        ]

    def create(self, validated_data):
        # Extract game_name and remove it from validated_data
        game_name = validated_data.pop('game_name')

        # Attempt to fetch the Game instance
        try:
            game = Game.objects.get(name=game_name)
        except Game.DoesNotExist:
            raise serializers.ValidationError({
                'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
            })

        # Assign the found game instance to the 'game' field in validated_data
        validated_data['game'] = game

        # Check if created_by is provided
        if 'created_by' not in validated_data:
            raise serializers.ValidationError({'created_by': 'This field is required.'})

        # Call the super class create method with updated validated_data
        return super().create(validated_data)
class DeckSerializerfordeck(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)  # Add this line to include card data

    class Meta:
        model = Deck
        fields = ['id', 'user', 'game', 'name', 'image','description', 'cards']  # Inclu
class DraftTournamentSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(write_only=True)  # Field for passing the game name


    class Meta:
        model = Tournament
        fields = [
            'id','tournament_name', 'email_address', 'contact_number','venue',
            'event_date', 'event_start_time', 'last_registration_date',
            'tournament_fee', 'banner_image', 'game_name', 'is_draft','is_active',
        ]

    def create(self, validated_data):
        # Extract game_name and remove it from validated_data
        game_name = validated_data.pop('game_name')

        # Attempt to fetch the Game instance
        try:
            game = Game.objects.get(name=game_name)
        except Game.DoesNotExist:
            raise serializers.ValidationError({
                'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
            })

        # Assign the found game instance to the 'game' field in validated_data
        validated_data['game'] = game

        # Set is_draft to True for draft tournaments
        validated_data['is_draft'] = True

        # Call the super class create method with updated validated_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Extract game_name if provided
        game_name = validated_data.pop('game_name', None)

        # Attempt to fetch the Game instance if game_name is provided
        if game_name:
            try:
                game = Game.objects.get(name=game_name)
                validated_data['game'] = game
            except Game.DoesNotExist:
                raise serializers.ValidationError({
                    'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
                })

        # Update the instance with the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'name','image']  # Include other fields if necessary

class getTournamentSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(source='game.name', read_only=True)  # Include game name

    class Meta:
        model = Tournament
        # Updated fields list with new fields
        fields = [
            'tournament_name', 'email_address', 'contact_number', 'venue',
            'event_date', 'event_start_time', 'last_registration_date',
            'tournament_fee', 'banner_image', 'game_name','is_active',
        ]
class ParticipantSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.tournament_name', read_only=True)
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    cards = serializers.SerializerMethodField()
    class Meta:
        model = Participant
        fields = ['id', 'user', 'tournament_name', 'deck_name', 'registration_date', 'payment_status', 'total_score','cards','is_ready']
    def get_cards(self, obj):
        if obj.deck:
            cards = Card.objects.filter(deck=obj.deck)
            return CardSerializer(cards, many=True).data
        return []
class ParticipantSerializerforfixture(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.tournament_name', read_only=True)
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    user = UserProfileSerializer()

    class Meta:
        model = Participant
        fields = ['id', 'user', 'tournament','tournament_name', 'deck_name', 'registration_date', 'payment_status', 'total_score','is_ready']

class TournamentSerializernew(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)  # Include participants
    game_name = serializers.CharField(source='game.name', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    createdby_user_image = serializers.CharField(source='created_by.image', read_only=True)
    class Meta:
        model = Tournament
        fields = [
            'id',
            'tournament_name',
            'email_address',
            'contact_number',
            'event_date',
            'event_start_time',
            'last_registration_date',
            'tournament_fee',
            'banner_image',
            'venue',
            'is_draft',
            'game_name',
            'created_by',
            'created_at',
            'featured',
            'participants' ,
            'is_active',
            'createdby_user_image'# Add this line
        ]
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Get the current request from the context
        request = self.context.get('request')

        # Define the base URL for media files
        base_url = "https://dueling.pythonanywhere.com/media/"

        # Construct the absolute URL for the image
        if 'createdby_user_image' in representation and representation['createdby_user_image']:
            representation['createdby_user_image'] = f"{base_url}{representation['createdby_user_image']}"

        return representation


class FeaturedTournamentSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()

    class Meta:
        model = FeaturedTournament
        fields = ['id', 'tournament', 'is_featured', 'featured_date']

class createFeaturedTournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedTournament
        fields = ['id', 'is_featured', 'featured_date']
class ParticipantSerializerforadminviewfixture(serializers.ModelSerializer):
    tournament = TournamentSerializernew()
    deck_name = serializers.CharField(source='deck.name', read_only=True)
    user = UserProfileSerializer()

    class Meta:
        model = Participant
        fields = ['id', 'user', 'tournament', 'deck_name', 'registration_date', 'payment_status', 'total_score','is_ready']
class BannerImageSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer()

    class Meta:
        model = BannerImage
        fields = ['id', 'tournament', 'image', 'uploaded_at']

class newBannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ['tournament', 'image']  # Include tournament ID and image field

    def validate_tournament(self, value):
        if not value:
            raise serializers.ValidationError("Tournament is required.")
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Image file is required.")
        return value

class DeckSerializercreate(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id','user', 'game', 'name','description', 'image']
class DeckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deck
        fields = ['id','user', 'game', 'name', 'image']  # Add other fields as needed

class ParticipantSerializernew(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()  # Dynamic field for participant count
    tournament = TournamentSerializernew()  # Nested tournament serializer
    deck = DeckSerializer()  # Nested deck serializer

    class Meta:
        model = Participant
        fields = [
            'id',
            'user',
            'tournament',
            'deck',
            'registration_date',
            'payment_status',
            'participant_count',
            'is_disqualified',
            'arrived_at_venue',
            'total_score',
            'is_ready'
        ]  # Specify only the fields you want to include for control over output

    def get_participant_count(self, obj):
        # Efficiently calculate the count of participants for the given tournament
        return Participant.objects.filter(tournament=obj.tournament).count()


class FixtureSerializer(serializers.ModelSerializer):
    participant1 = ParticipantSerializerforfixture()
    participant2 = ParticipantSerializerforfixture(allow_null=True)  # Allow null for participant2


    class Meta:
        model = Fixture
        fields = ['id', 'tournament', 'participant1', 'participant2', 'round_number', 'match_date', 'nominated_winner', 'verified_winner', 'is_verified','start_time','is_tournament_completed']
class FixtureSerializernew(serializers.ModelSerializer):
    participant1 = ParticipantSerializer()
    participant2 = ParticipantSerializer(allow_null=True)  # Allow null for participant2


    class Meta:
        model = Fixture
        fields = ['id', 'tournament', 'participant1', 'participant2', 'round_number', 'match_date', 'nominated_winner', 'verified_winner', 'is_verified','start_time','is_tournament_completed']





class ParticipantSerializernewforactivelist(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()  # Dynamic field for participant count
    tournament = TournamentSerializernew()  # Nested tournament serializer
    deck = DeckSerializer()
    user=UserProfileSerializer() # Nested deck serializer

    class Meta:
        model = Participant
        fields = [
            'id',
            'user',
            'tournament',
            'deck',
            'registration_date',
            'payment_status',
            'participant_count',
            'is_disqualified',
            'arrived_at_venue',
            'total_score',
            'is_ready'
        ]  # Specify only the fields you want to include for control over output

    def get_participant_count(self, obj):
        # Efficiently calculate the count of participants for the given tournament
        return Participant.objects.filter(tournament=obj.tournament).count()


class MatchScoreSerializer(serializers.ModelSerializer):
    Participant=UserProfileSerializer()
    class Meta:
        model = MatchScore
        fields = ['id', 'participant', 'tournament', 'rank', 'round', 'win', 'lose', 'score']



class newMatchScoreSerializer(serializers.ModelSerializer):
    participant = serializers.CharField(source='participant.user.username', read_only=True)  # Directly access username from related Participant
    tournament_name = serializers.CharField(source='tournament.tournament_name', read_only=True)  # Access tournament name from related Tournament

    class Meta:
        model = MatchScore
        fields = ['id', 'participant', 'tournament_name', 'rank', 'round', 'win', 'lose', 'score']

# class newMatchScoreSerializer(serializers.ModelSerializer):
    
#     participant=UserProfileSerializer()
#     class Meta:
#         model = MatchScore
#         fields = ['id', 'participant', 'tournament', 'rank', 'round', 'win', 'lose', 'score']






# class TournamentSerializerhistory(serializers.ModelSerializer):
#     participants = ParticipantSerializer(many=True, read_only=True)  # Include participants
#     game_name = serializers.CharField(source='game.name', read_only=True)
#     created_by = serializers.CharField(source='created_by.username', read_only=True)
#     createdby_user_image = serializers.CharField(source='created_by.image', read_only=True)
#     leaderboard = serializers.SerializerMethodField()

#     class Meta:
#         model = Tournament
#         fields = [
#             'id',
#             'tournament_name',
#             'email_address',
#             'contact_number',
#             'event_date',
#             'event_start_time',
#             'last_registration_date',
#             'tournament_fee',
#             'banner_image',
#             'venue',
#             'is_draft',
#             'game_name',
#             'created_by',
#             'created_at',
#             'featured',
#             'participants',
#             'is_active',
#             'createdby_user_image',
#             'leaderboard',  # Add leaderboard field
#         ]

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)

#         # Get the current request from the context
#         request = self.context.get('request')

#         # Define the base URL for media files
#         base_url = "https://dueling.pythonanywhere.com/media/"

#         # Construct the absolute URL for the image
#         if 'createdby_user_image' in representation and representation['createdby_user_image']:
#             representation['createdby_user_image'] = f"{base_url}{representation['createdby_user_image']}"

#         return representation

#     def get_leaderboard(self, instance):
#         """
#         Get the leaderboard for the tournament sorted by participant scores
#         based on the MatchScore table.
#         """
#         # Get all participants for the tournament
#         participants = instance.participants.all()

#         leaderboard = []

#         # Calculate total score for each participant by summing their scores in MatchScore
#         for participant in participants:
#             # Get all match scores for this participant in this tournament
#             match_scores = MatchScore.objects.filter(participant=participant, tournament=instance)

#             total_score = sum(match.score for match in match_scores)  # Sum the scores

#             leaderboard.append({
#                 'user': participant.user.username,  # Participant's username
#                 'total_score': total_score,  # Total score from all matches
#                 'rank': 0  # Placeholder for now, will calculate rank later
#             })

#         # Sort the leaderboard by total_score in descending order
#         leaderboard = sorted(leaderboard, key=lambda x: x['total_score'], reverse=True)

#         # Assign ranks based on the sorted leaderboard
#         for index, entry in enumerate(leaderboard):
#             entry['rank'] = index + 1  # Rank starts from 1

#         return leaderboard
class ParticipantSerializernewhistory(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()  # Dynamic field for participant count
    tournament = TournamentSerializernew()  # Nested tournament serializer
    deck = DeckSerializer()  # Nested deck serializer
     # Dynamic field for leaderboard rank

    class Meta:
        model = Participant
        fields = [
            'id',
            'user',
            'tournament',
            'deck',
            'registration_date',
            'payment_status',
            'participant_count',
            'is_disqualified',
            'arrived_at_venue',
            'total_score',
            'is_ready',
             # Include the new leaderboard field
        ]

    def get_participant_count(self, obj):
        # Efficiently calculate the count of participants for the given tournament
        return Participant.objects.filter(tournament=obj.tournament).count()

class ParticipantSerializernewforactivelist(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()  # Dynamic field for participant count
    tournament = TournamentSerializernew()  # Nested tournament serializer
    deck = DeckSerializer()
    user=UserProfileSerializer() # Nested deck serializer

    class Meta:
        model = Participant
        fields = [
            'id',
            'user',
            'tournament',
            'deck',
            'registration_date',
            'payment_status',
            'participant_count',
            'is_disqualified',
            'arrived_at_venue',
            'total_score',
            'is_ready'
        ]  # Specify only the fields you want to include for control over output

    def get_participant_count(self, obj):
        # Efficiently calculate the count of participants for the given tournament
        return Participant.objects.filter(tournament=obj.tournament).count()
class DeckSerializerdetail(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)  # Nested serializer to display cards associated with the deck

    class Meta:
        model = Deck
        fields = [
            'id',
            'user',
            'game',
            'name',
            'image',
            'description',
            'cards'  # Include the cards for each deck
        ]

class TopPlayerSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    user_profile = UserProfileSerializer()