# serializers.py
from rest_framework import serializers
from .models import *
from users.serializers import UserProfileSerializer

from rest_framework import serializers
from .models import Tournament, Game,Deck,Participant,Fixture,MatchScore
from users.models import User
from rest_framework import serializers
from django.conf import settings
from .models import Tournament, Participant, MatchScore


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['payment_status']

    def validate_payment_status(self, value):
        valid_choices = [choice[0] for choice in Participant.PAYMENT_STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid payment status. Choose from {valid_choices}.")
        return value
class TournamentUpdateprizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['round_time', 'first_prize', 'second_prize', 'third_prize']
class StaffSerializern(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')  # Serialize username of the associated user
    role = serializers.CharField()  # Serialize the role field
    is_active = serializers.BooleanField()  # Serialize the is_active field

    class Meta:
        model = Staff
        fields = ['id','user', 'role', 'is_active']
class StaffSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')  # Serialize username of the associated user
    role = serializers.CharField()  # Serialize the role field
    is_active = serializers.BooleanField()  # Serialize the is_active field

    class Meta:
        model = Staff
        fields = ['user', 'role', 'is_active']



class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
# class TournamentSerializer(serializers.ModelSerializer):
#     game_name = serializers.CharField(write_only=True)  # Field for passing the game name
#     created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # User creating the tournament

#     class Meta:
#         model = Tournament
#         fields = [
#             'id','tournament_name', 'email_address', 'contact_number',
#             'event_date', 'event_start_time', 'last_registration_date',
#             'tournament_fee', 'banner_image', 'venue','game_name', 'is_draft', 'created_by','created_at','featured','is_active',
#         ]

#     def create(self, validated_data):
#         # Extract game_name and remove it from validated_data
#         game_name = validated_data.pop('game_name')

#         # Attempt to fetch the Game instance
#         try:
#             game = Game.objects.get(name=game_name)
#         except Game.DoesNotExist:
#             raise serializers.ValidationError({
#                 'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
#             })

#         # Assign the found game instance to the 'game' field in validated_data
#         validated_data['game'] = game

#         # Check if created_by is provided
#         if 'created_by' not in validated_data:
#             raise serializers.ValidationError({'created_by': 'This field is required.'})

#         # Call the super class create method with updated validated_data
#         return super().create(validated_data)
# class TournamentSerializer(serializers.ModelSerializer):
#     game_name = serializers.CharField(write_only=True)  # Field for passing the game name
#     created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # User creating the tournament

#     class Meta:
#         model = Tournament
#         fields = [
#             'id', 'tournament_name', 'email_address', 'contact_number',
#             'event_date', 'event_start_time', 'last_registration_date',
#             'tournament_fee', 'banner_image', 'venue', 'game_name', 'is_draft',
#             'created_by', 'created_at', 'featured', 'is_active',
#         ]

#     def create(self, validated_data):
#         # Extract game_name and remove it from validated_data
#         game_name = validated_data.pop('game_name')

#         # Attempt to fetch the Game instance
#         try:
#             game = Game.objects.get(name=game_name)
#         except Game.DoesNotExist:
#             raise serializers.ValidationError({
#                 'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
#             })

#         # Assign the found game instance to the 'game' field in validated_data
#         validated_data['game'] = game

#         # Set `is_active` to True explicitly
#         validated_data['is_active'] = True

#         # Check if created_by is provided
#         if 'created_by' not in validated_data:
#             raise serializers.ValidationError({'created_by': 'This field is required.'})

#         # Call the super class create method with updated validated_data
#         return super().create(validated_data)
class TournamentSerializerforfeature(serializers.ModelSerializer):
    game_name = serializers.CharField(write_only=True, help_text="Name of the game to associate with the tournament")
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        help_text="User ID creating the tournament"
    )
    staff_ids = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="IDs of staff members associated with the tournament"
    )
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    tournament_style_display = serializers.CharField(source='get_tournament_style_display', read_only=True)
    tournament_structure_display = serializers.CharField(source='get_tournament_structure_display', read_only=True)
    player_structure_display = serializers.CharField(source='get_player_structure_display', read_only=True)
    banner_image = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = [
            'id', 'tournament_name', 'email_address', 'contact_number', 'event_date', 'event_start_time',
            'last_registration_date', 'tournament_fee', 'banner_image', 'venue', 'game_name', 'is_draft',
            'created_by', 'created_at', 'featured', 'is_active', 'event_type', 'tournament_style',
            'tournament_structure', 'player_structure', 'event_type_display', 'tournament_style_display',
            'tournament_structure_display', 'player_structure_display', 'staff_ids',
        ]
        read_only_fields = ['created_at', 'is_active', 'event_type_display', 'tournament_style_display',
                            'tournament_structure_display', 'player_structure_display']

    def get_banner_image(self, obj):
        if obj.banner_image:
            return f"{settings.MEDIA_URL}{obj.banner_image}"
        return None

    def create(self, validated_data):
        # Extract game_name and staff_ids from validated_data
        print("Validating data:", validated_data)  # Print the entire validated data
        game_name = validated_data.pop('game_name')
        staff_ids = validated_data.pop('staff_ids', [])

        print(f"Game Name: {game_name}")  # Print the game name being processed
        print(f"Staff IDs: {staff_ids}")  # Print the staff IDs being processed

        # Retrieve the Game instance by name
        try:
            game = Game.objects.get(name=game_name)
            print(f"Game found: {game.name}")  # Print the game found in the database
        except Game.DoesNotExist:
            print(f"Game with name '{game_name}' does not exist.")  # Print error if game doesn't exist
            raise serializers.ValidationError({
                'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
            })

        # Add the fetched game instance to validated_data
        validated_data['game'] = game

        # Ensure `is_active` is explicitly set to True
        validated_data['is_active'] = True
        print(f"Validated data after adding game and is_active: {validated_data}")  # Print after adding game and is_active

        # Validate the presence of `created_by`
        if 'created_by' not in validated_data:
            print("Created_by field is missing!")  # Print message if created_by is missing
            raise serializers.ValidationError({'created_by': 'This field is required.'})

        # Create the Tournament instance
        print("Creating tournament instance...")  # Print before creating the tournament instance
        tournament = super().create(validated_data)

        # Assign staff to the tournament if staff_ids is provided
        if staff_ids:
            print(f"Assigning staff: {staff_ids}")  # Print the staff IDs being assigned to the tournament
            tournament.staff.set(staff_ids)

        print(f"Tournament created with ID: {tournament.id}")  # Print the ID of the created tournament
        return tournament

class TournamentSerializer(serializers.ModelSerializer):
    game_name = serializers.CharField(write_only=True, help_text="Name of the game to associate with the tournament")
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        help_text="User ID creating the tournament"
    )
    staff_ids = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="IDs of staff members associated with the tournament"
    )
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    tournament_style_display = serializers.CharField(source='get_tournament_style_display', read_only=True)
    tournament_structure_display = serializers.CharField(source='get_tournament_structure_display', read_only=True)
    player_structure_display = serializers.CharField(source='get_player_structure_display', read_only=True)
    banner_image = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Tournament
        fields = [
            'id', 'tournament_name', 'email_address', 'contact_number', 'event_date', 'event_start_time',
            'last_registration_date', 'tournament_fee', 'banner_image', 'venue', 'game_name', 'is_draft',
            'created_by', 'created_at', 'featured', 'is_active', 'event_type', 'tournament_style',
            'tournament_structure', 'player_structure', 'event_type_display', 'tournament_style_display',
            'tournament_structure_display', 'player_structure_display', 'staff_ids',
        ]
        read_only_fields = ['created_at', 'is_active', 'event_type_display', 'tournament_style_display',
                            'tournament_structure_display', 'player_structure_display']

    def create(self, validated_data):
        # Extract game_name and staff_ids from validated_data
        print("Validating data:", validated_data)  # Print the entire validated data
        game_name = validated_data.pop('game_name')
        staff_ids = validated_data.pop('staff_ids', [])

        print(f"Game Name: {game_name}")  # Print the game name being processed
        print(f"Staff IDs: {staff_ids}")  # Print the staff IDs being processed

        # Retrieve the Game instance by name
        try:
            game = Game.objects.get(name=game_name)
            print(f"Game found: {game.name}")  # Print the game found in the database
        except Game.DoesNotExist:
            print(f"Game with name '{game_name}' does not exist.")  # Print error if game doesn't exist
            raise serializers.ValidationError({
                'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
            })

        # Add the fetched game instance to validated_data
        validated_data['game'] = game

        # Ensure `is_active` is explicitly set to True
        validated_data['is_active'] = True
        print(f"Validated data after adding game and is_active: {validated_data}")  # Print after adding game and is_active

        # Validate the presence of `created_by`
        if 'created_by' not in validated_data:
            print("Created_by field is missing!")  # Print message if created_by is missing
            raise serializers.ValidationError({'created_by': 'This field is required.'})

        # Create the Tournament instance
        print("Creating tournament instance...")  # Print before creating the tournament instance
        tournament = super().create(validated_data)

        # Assign staff to the tournament if staff_ids is provided
        if staff_ids:
            print(f"Assigning staff: {staff_ids}")  # Print the staff IDs being assigned to the tournament
            tournament.staff.set(staff_ids)

        print(f"Tournament created with ID: {tournament.id}")  # Print the ID of the created tournament
        return tournament

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


class TournamentSerializerupdate(serializers.ModelSerializer):
    game_name = serializers.CharField(write_only=True, help_text="Name of the game to associate with the tournament")
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        help_text="User ID creating the tournament"
    )
    staff = StaffSerializer(many=True, read_only=True)  # Use the StaffSerializer to include staff data
    staff_ids = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        many=True,
        write_only=True,
        required=False,
        help_text="IDs of staff members associated with the tournament"
    )
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    tournament_style_display = serializers.CharField(source='get_tournament_style_display', read_only=True)
    tournament_structure_display = serializers.CharField(source='get_tournament_structure_display', read_only=True)
    player_structure_display = serializers.CharField(source='get_player_structure_display', read_only=True)

    class Meta:
        model = Tournament
        fields = [
            'id', 'tournament_name', 'email_address', 'contact_number', 'event_date', 'event_start_time',
            'last_registration_date', 'tournament_fee', 'banner_image', 'venue', 'game_name', 'is_draft',
            'created_by', 'created_at', 'featured', 'is_active', 'event_type', 'tournament_style',
            'tournament_structure', 'player_structure', 'event_type_display', 'tournament_style_display',
            'tournament_structure_display', 'player_structure_display', 'staff', 'staff_ids',
        ]
        read_only_fields = ['created_at', 'is_active', 'event_type_display', 'tournament_style_display',
                            'tournament_structure_display', 'player_structure_display']

    def create(self, validated_data):
        # Extract game_name and staff_ids from validated_data
        print("Validating data:", validated_data)  # Print the entire validated data
        game_name = validated_data.pop('game_name')
        staff_ids = validated_data.pop('staff_ids', [])

        print(f"Game Name: {game_name}")  # Print the game name being processed
        print(f"Staff IDs: {staff_ids}")  # Print the staff IDs being processed

        # Retrieve the Game instance by name
        try:
            game = Game.objects.get(name=game_name)
            print(f"Game found: {game.name}")  # Print the game found in the database
        except Game.DoesNotExist:
            print(f"Game with name '{game_name}' does not exist.")  # Print error if game doesn't exist
            raise serializers.ValidationError({
                'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
            })

        # Add the fetched game instance to validated_data
        validated_data['game'] = game

        # Ensure `is_active` is explicitly set to True
        validated_data['is_active'] = True
        print(f"Validated data after adding game and is_active: {validated_data}")  # Print after adding game and is_active

        # Validate the presence of `created_by`
        if 'created_by' not in validated_data:
            print("Created_by field is missing!")  # Print message if created_by is missing
            raise serializers.ValidationError({'created_by': 'This field is required.'})

        # Create the Tournament instance
        print("Creating tournament instance...")  # Print before creating the tournament instance
        tournament = super().create(validated_data)

        # Assign staff to the tournament if staff_ids is provided
        if staff_ids:
            print(f"Assigning staff: {staff_ids}")  # Print the staff IDs being assigned to the tournament
            tournament.staff.set(staff_ids)

        print(f"Tournament created with ID: {tournament.id}")  # Print the ID of the created tournament
        return tournament
    def update(self, instance, validated_data):
        # Extract game_name and staff_ids from validated_data
        game_name = validated_data.pop('game_name', None)
        staff_ids = validated_data.pop('staff_ids', None)

        # Retrieve the Game instance by name if game_name is provided
        if game_name:
            try:
                game = Game.objects.get(name=game_name)
            except Game.DoesNotExist:
                raise serializers.ValidationError({
                    'game_name': f"A game with the name '{game_name}' does not exist. Please provide a valid game name."
                })
            validated_data['game'] = game

        # Ensure `is_active` is explicitly set to True
        validated_data['is_active'] = instance.is_active  # Preserve the current value of `is_active`

        # Update the Tournament instance with validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update staff if staff_ids is provided
        if staff_ids is not None:
            instance.staff.set(staff_ids)

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

# class TournamentSerializernew(serializers.ModelSerializer):
#     participants = ParticipantSerializer(many=True, read_only=True)  # Include participants
#     game_name = serializers.CharField(source='game.name', read_only=True)
#     created_by = serializers.CharField(source='created_by.username', read_only=True)
#     createdby_user_image = serializers.CharField(source='created_by.image', read_only=True)
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
#             'participants' ,
#             'is_active',
#             'createdby_user_image'# Add this line
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
 # Adjust fields as necessary
 # Adjust the fields as needed

class TournamentSerializernew(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)  # Include participants
    game_name = serializers.CharField(source='game.name', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    createdby_user_image = serializers.CharField(source='created_by.image', read_only=True)
    event_type = serializers.CharField(source='get_event_type_display', read_only=True)  # Readable event type
    tournament_style = serializers.CharField(source='get_tournament_style_display', read_only=True)  # Readable tournament style
    tournament_structure = serializers.CharField(source='get_tournament_structure_display', read_only=True)  # Readable tournament structure
    player_structure = serializers.CharField(source='get_player_structure_display', read_only=True)  # Readable player structure
    staff = StaffSerializern(many=True, read_only=True)  # Include staff

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
            'participants',
            'is_active',
            'createdby_user_image',
            'event_type',  # Added event type
            'tournament_style',  # Added tournament style
            'tournament_structure',  # Added tournament structure
            'player_structure',  # Added player structure
            'staff',  # Added staff
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
# class BannerImageSerializer(serializers.ModelSerializer):
#     tournament = TournamentSerializer()

#     class Meta:
#         model = BannerImage
#         fields = ['id', 'tournament', 'image', 'uploaded_at']

# class newBannerImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BannerImage
#         fields = ['tournament', 'image']  # Include tournament ID and image field

#     def validate_tournament(self, value):
#         if not value:
#             raise serializers.ValidationError("Tournament is required.")
#         return value

#     def validate_image(self, value):
#         if not value:
#             raise serializers.ValidationError("Image file is required.")
#         return value

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
from datetime import datetime, date
from django.utils import timezone
class SwissFixtureSerializerforfixture(serializers.ModelSerializer):
    participant1 = ParticipantSerializerforfixture()
    participant2 = ParticipantSerializerforfixture(allow_null=True)  # Allow null for participant2
    # Handle datetime properly

    class Meta:
        model = SwissFixture
        fields = [
            'id',
            'tournament',
            'participant1',
            'participant2',
            'round_number',
            'match_date',
            'nominated_winner',
            'verified_winner',
            'is_verified',
            'start_time',
            'is_tournament_completed',
            'participant1_score',
            'participant2_score',
            'draw','nominated_winner', 'verified_winner', 'is_verified','start_time','is_tournament_completed',
        ]
class SwissFixtureSerializer(serializers.ModelSerializer):
    participant1 = ParticipantSerializerforfixture()
    participant2 = ParticipantSerializerforfixture(allow_null=True)  # Allow null for participant2
    # Handle datetime properly

    class Meta:
        model = SwissFixture
        fields = [
            'id',
            'tournament',
            'participant1',
            'participant2',
            'round_number',
            'nominated_winner',
            'verified_winner',
            'is_verified',
            'start_time',
            'is_tournament_completed',
            'participant1_score',
            'participant2_score',
            'draw','nominated_winner', 'verified_winner', 'is_verified','start_time','is_tournament_completed',
        ]





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



# class SwissFixtureSerializer(serializers.ModelSerializer):
#     # Adding readable nested fields for foreign keys
#     tournament_name = serializers.CharField(source='tournament.name', read_only=True)
#     participant1_name = serializers.CharField(source='participant1.name', read_only=True)
#     participant2_name = serializers.CharField(source='participant2.name', read_only=True)
#     nominated_winner_name = serializers.CharField(source='nominated_winner.name', read_only=True, required=False)
#     verified_winner_name = serializers.CharField(source='verified_winner.name', read_only=True, required=False)

#     class Meta:
#         model = SwissFixture
#         fields = [
#             'id', 'tournament', 'participant1', 'participant2', 'round_number', 'match_date',
#             'start_time', 'nominated_winner', 'verified_winner', 'is_verified', 'is_tournament_completed',
#             'tournament_name', 'participant1_name', 'participant2_name', 'nominated_winner_name', 'verified_winner_name','draw',
#         ]


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
class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ['title', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']
class BannerImageSerializernew(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ['id','title', 'image', 'uploaded_at']
        read_only_fields = ['uploaded_at']

# class CreateBannerImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BannerImage
#         fields = ['id', 'tournament', 'image']

#     def validate(self, data):
#         # Validate that the tournament exists
#         if not Tournament.objects.filter(id=data['tournament'].id).exists():
#             raise serializers.ValidationError("Invalid tournament ID")

#         # Validate that the image is provided
#         if 'image' not in data:
#             raise serializers.ValidationError("Image is required")

#         return data

#     def create(self, validated_data):
#         return BannerImage.objects.create(**validated_data)