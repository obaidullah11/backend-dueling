# views.py
from rest_framework import generics
from rest_framework import status
from .models import Fixture, Participant, MatchScore, Tournament
from rest_framework.views import APIView
from .serializers import *
from firebase_admin import credentials, firestore
from django.shortcuts import get_object_or_404
from .utils import api_response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Tournament
from django.utils.timezone import now
import pytz  # To handle time zones
from .serializers import  MatchScoreSerializer,FixtureSerializernew, CardSerializer,DeckSerializercreate,TournamentSerializer,TournamentSerializernew, DraftTournamentSerializer,ParticipantSerializer,ParticipantSerializernew,ParticipantSerializernewforactivelist
import random
from datetime import datetime, timedelta
import requests
from collections import defaultdict
from django.utils.timezone import activate, localtime
import pytz

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone






from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count
from .models import Fixture, Participant
from .serializers import FixtureSerializer,MatchScoreSerializer
class TopPlayersView(APIView):
    def get(self, request):
        # Fetching top 10 players with win and loss counts
        players = (
            Participant.objects
            .values('user')
            .annotate(
                wins=Count('matchscore', filter=Q(matchscore__win=True)),
                losses=Count('matchscore', filter=Q(matchscore__lose=True))
            )
            .order_by('-wins')[:10]
        )

        result = []
        for player in players:
            user = player['user']  # This is likely the user ID or string, not the User object
            user_instance = User.objects.get(id=user)  # Fetch the actual User object

            # Serialize the UserProfile data
            user_profile_data = UserProfileSerializer(user_instance).data  # Pass the actual User object here

            result.append({
                'player_name': user_instance.username,  # Use the actual user instance here
                'wins': player['wins'],
                'losses': player['losses'],
                'user_profile': user_profile_data  # Serialize the actual User object
            })

        return Response({
            'success': True,
            'data': result
        })
class TournamentMatchScoresView(APIView):
    def get(self, request, tournament_id):
        try:
            # Fetch the tournament by ID
            tournament = Tournament.objects.get(id=tournament_id)

            # Fetch all match scores for the given tournament
            match_scores = MatchScore.objects.filter(tournament=tournament)

            # Sort the match scores by score in descending order
            sorted_match_scores = sorted(match_scores, key=lambda x: x.score, reverse=True)

            # Assign ranks based on sorted scores
            ranked_scores = []
            for rank, match_score in enumerate(sorted_match_scores, start=1):
                ranked_scores.append({
                    'id': match_score.id,
                    'participant_name': match_score.participant.user.username,
                    'tournament_name': match_score.tournament.tournament_name,
                    'round': match_score.round,
                    'rank': match_score.rank,
                    'rank_number': rank,  # Add the rank_number
                    'win': match_score.win,
                    'lose': match_score.lose,
                    'score': match_score.score
                })

            return Response({
                "success": True,
                "message": "Match scores with ranks retrieved successfully.",
                "data": ranked_scores
            }, status=status.HTTP_200_OK)

        except Tournament.DoesNotExist:
            return Response({
                "success": False,
                "message": "Tournament not found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
class UserInactiveTournamentsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            # Ensure you correctly filter by the 'active' field of the related 'tournament' model
            participants = Participant.objects.filter(
                user=user,
                tournament__is_active=False  # This is valid if 'active' is a boolean field on Tournament
            )

            # Serialize the data with leaderboard rank
            serializer = ParticipantSerializernewhistory(participants, many=True)

            return Response({
                "success": True,
                "message": "Inactive tournaments retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)



class DeckByNameView(APIView):
    def get(self, request, deck_name):
        try:
            # Fetch the deck by name
            deck = Deck.objects.get(name=deck_name)

            # Serialize the deck and its associated cards
            serializer = DeckSerializerdetail(deck)

            return Response({
                "success": True,
                "message": "Deck data retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Deck.DoesNotExist:
            return Response({
                "success": False,
                "message": "Deck not found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
def get_match_scores_by_tournament(request, tournament_id):
    try:
        # Fetch all match scores for the given tournament_id
        match_scores = MatchScore.objects.filter(tournament_id=tournament_id)

        if not match_scores:
            return Response({
                "success": False,
                "message": "No match scores found for this tournament.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the match scores data
        serialized_data = MatchScoreSerializer(match_scores, many=True)

        return Response({
            "success": True,
            "message": "Match scores fetched successfully",
            "data": serialized_data.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class adminstartmatch(APIView):
    def post(self, request, tournament_id):
        try:
            # Get the tournament instance by ID
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"success": False, "message": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update all fixtures related to the tournament where start_time is False
        fixtures_updated = Fixture.objects.filter(tournament=tournament, start_time=False).update(start_time=True)

        return Response({
            "success": True,
            "message": f"{fixtures_updated} fixtures updated to start.",
            "data": {
                "tournament_id": tournament_id,
                "fixtures_updated_count": fixtures_updated,
            }
        }, status=status.HTTP_200_OK)
class UpdateParticipantReadyStatus(APIView):
    def post(self, request, participant_id):
        try:
            # Get the participant instance by ID
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            return Response({"success": False, "message": "Participant not found."}, status=status.HTTP_404_NOT_FOUND)

        # Set is_ready to True
        participant.is_ready = True
        participant.save()

        # Prepare response data
        data = {
            "id": participant.id,
            "user": participant.user.username,
            "tournament": participant.tournament.tournament_name,
            "is_ready": participant.is_ready,
            "payment_status": participant.payment_status,
            "total_score": participant.total_score,
        }

        return Response({
            "success": True,
            "message": "Participant status updated to ready.",
            "data": data
        }, status=status.HTTP_200_OK)

# class admingetallTournamentFixturesView(APIView):
#     def get(self, request, tournament_id):
#         try:
#             # Check if tournament exists
#             tournament = Tournament.objects.get(id=tournament_id)

#             # Get all fixtures for the tournament
#             fixtures = Fixture.objects.filter(tournament=tournament)

#             # Serialize the fixtures
#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({
#                 "success": True,
#                 "message": "Fixtures retrieved successfully.",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Tournament.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Tournament not found."
#             }, status=status.HTTP_404_NOT_FOUND)


class admingetallTournamentFixturesView(APIView):
    def get(self, request, tournament_id):
        try:
            # Check if tournament exists
            tournament = Tournament.objects.get(id=tournament_id)

            # Get all fixtures for the tournament
            fixtures = Fixture.objects.filter(tournament=tournament)

            # Serialize the fixtures
            serializer = FixtureSerializer(fixtures, many=True)

            # Group fixtures by round number
            grouped_fixtures = defaultdict(list)
            for fixture in serializer.data:
                round_number = fixture['round_number']
                grouped_fixtures[round_number].append(fixture)

            # Prepare the rounds array
            rounds = [{"round_number": round_num, "fixtures": fixtures} for round_num, fixtures in grouped_fixtures.items()]

            return Response({
                "success": True,
                "message": "Fixtures retrieved successfully.",
                "data": rounds
            }, status=status.HTTP_200_OK)

        except Tournament.DoesNotExist:
            return Response({
                "success": False,
                "message": "Tournament not found."
            }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def eliminate_participant(request, fixture_id):
    print(f"Received request to eliminate participant from fixture ID: {fixture_id}")

    # Fetch the fixture based on the given ID
    try:
        fixture = Fixture.objects.get(id=fixture_id)
        print(f"Fixture found: {fixture}")
    except Fixture.DoesNotExist:
        print(f"Fixture with ID {fixture_id} does not exist.")
        return Response({"success": False, "message": "Fixture not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)

    # Get the participant ID from the request data
    participant_id = request.data.get("participant_id")
    print(f"Participant ID to eliminate: {participant_id}")

    # Check if participant_id was provided
    if not participant_id:
        print("No participant_id provided in the request.")
        return Response({"success": False, "message": "participant_id not provided", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the participant based on the given ID
    try:
        participant = Participant.objects.get(id=participant_id)
        print(f"Participant found: {participant}")

        # Mark the participant as disqualified
        participant.is_disqualified = True
        participant.save()
        print(f"Participant {participant} has been marked as disqualified.")

        # Set the opponent as the nominated winner
        if fixture.participant1 == participant:
            winner = fixture.participant2
        else:
            winner = fixture.participant1

        fixture.nominated_winner = winner
        fixture.verified_winner = winner
        fixture.is_verified = True
        fixture.save()
        print(f"Nominated winner set to: {winner}")

        data = FixtureSerializer(fixture).data

        return Response({"success": True, "message": "Participant eliminated and opponent set as winner", "data": data}, status=status.HTTP_200_OK)

    except Participant.DoesNotExist:
        print(f"Participant with ID {participant_id} does not exist.")
        return Response({"success": False, "message": "Invalid participant_id", "data": {}}, status=status.HTTP_404_NOT_FOUND)

















class TodayEventParticipantsView(APIView):
    def get(self, request, user_id):
        # Get today's date
        today = timezone.now().date()
        print(f"Today's date: {today}")

        # Filter tournaments created by the given user and with today's event date
        tournaments = Tournament.objects.filter(created_by=user_id, event_date=today)

        # Prepare response data
        response_data = []

        for tournament in tournaments:
            # Get participants for the tournament
            paid_participants = Participant.objects.filter(tournament=tournament, is_disqualified=False)
            disqualified_participants = Participant.objects.filter(tournament=tournament, is_disqualified=True)

            # Serialize tournament and participants data
            tournament_data = TournamentSerializernew(tournament).data
            paid_participants_data = ParticipantSerializer(paid_participants, many=True).data
            disqualified_participants_data = ParticipantSerializer(disqualified_participants, many=True).data

            # Organize tournament details with participants into response format
            tournament_data.update({
                "paid_participants": paid_participants_data,
                "disqualified_participants": disqualified_participants_data,
            })
            response_data.append(tournament_data)
            print(f"Tournament: {tournament_data}")
            print(f"Paid participants: {paid_participants_data}")
            print(f"Disqualified participants: {disqualified_participants_data}")

        # Set response status based on the presence of data
        if response_data:
            response = {
                "success": True,
                "message": "Today's event participants retrieved successfully.",
                "data": response_data
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "success": False,
                "message": "No events found for today.",
                "data": []
            }
            return Response(response, status=status.HTTP_200_OK)




@api_view(['GET'])
def events_today(request, user_id):
    """
    API to get paid events for a user that are scheduled for today.
    Expects 'user_id' as a URL parameter.
    """
    try:
        # Activate the timezone
        activate(pytz.timezone("Asia/Karachi"))

        # Current time and date in the set timezone
        current_time = localtime()
        current_date = current_time.date()

        # Filter participants
        participants = Participant.objects.filter(
            user_id=user_id,
            tournament__is_active=True,
            tournament__event_date=current_date,
            payment_status='paid'
        )

        # Serialize the participants
        serializer = ParticipantSerializernew(participants, many=True)

        return Response({
            'success': True,
            'message': "Paid tournaments retrieved successfully.",
            'data': serializer.data,
            'timezone': "Asia/Karachi",
            'current_date': current_date.strftime('%Y-%m-%d'),
            'current_time': current_time.strftime('%H:%M:%S')
        }, status=status.HTTP_200_OK)

    except Participant.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No paid tournaments found for today.',
            'data': [],
            'timezone': "Asia/Karachi",
            'current_date': current_time.date().strftime('%Y-%m-%d'),
            'current_time': current_time.strftime('%H:%M:%S')
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'data': [],
            'timezone': "Asia/Karachi",
            'current_date': current_time.date().strftime('%Y-%m-%d'),
            'current_time': current_time.strftime('%H:%M:%S')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET'])
# def events_today(request, user_id):
#     """
#     API to get paid events for a user that are scheduled for today.
#     Expects 'user_id' as a URL parameter.
#     """
#     try:
#         today = timezone.now().date()
#         participants = Participant.objects.filter(
#             user_id=user_id,
#             tournament__event_date=today,
#             payment_status='paid'
#         )

#         # Use the ParticipantSerializernew to serialize the participants
#         serializer = ParticipantSerializernew(participants, many=True)

#         return Response({
#             'success': True,
#             'message': "Paid tournaments retrieved successfully.",
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)

#     except Participant.DoesNotExist:
#         return Response({
#             'success': False,
#             'message': 'User or tournament not found.',
#             'data': []
#         }, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({
#             'success': False,
#             'message': str(e),
#             'data': []
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer  # Assuming you have a Participant serializer

    @action(detail=False, methods=['get'], url_path='events-today')
    def events_today(self, request):
        """
        API to get paid events for a user that are scheduled for today.
        Expects a 'user_id' parameter in the query string.
        """
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({
                'success': False,
                'message': 'User ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            today = timezone.now().date()
            participants = Participant.objects.filter(
                user_id=user_id,
                tournament__event_date=today,
                payment_status='paid'
            )
            tournaments = [participant.tournament for participant in participants]
            serializer = TournamentSerializer(tournaments, many=True)
            return Response({
                'success': True,
                'tournaments': serializer.data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def set_nominated_winner(request, fixture_id):
    try:
        fixture = Fixture.objects.get(id=fixture_id)
    except Fixture.DoesNotExist:
        return Response({"success": False, "message": "Fixture not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)

    winner_id = request.data.get("winner_id")
    if not winner_id:
        return Response({"success": False, "message": "winner_id not provided", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

    try:
        winner = Participant.objects.get(id=winner_id)
        fixture.nominated_winner = winner
        fixture.save()
        data = FixtureSerializer(fixture).data
        return Response({"success": True, "message": "Nominated winner set successfully", "data": data}, status=status.HTTP_200_OK)
    except Participant.DoesNotExist:
        return Response({"success": False, "message": "Invalid winner_id", "data": {}}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def set_verified_winner(request, fixture_id):
#     try:
#         fixture = Fixture.objects.get(id=fixture_id)
#     except Fixture.DoesNotExist:
#         return Response({"success": False, "message": "Fixture not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)

#     winner_id = request.data.get("winner_id")
#     if not winner_id:
#         return Response({"success": False, "message": "winner_id not provided", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         winner = Participant.objects.get(id=winner_id)
#         fixture.verified_winner = winner
#         fixture.is_verified = True
#         fixture.save()
#         data = FixtureSerializer(fixture).data
#         return Response({"success": True, "message": "Verified winner set successfully", "data": data}, status=status.HTTP_200_OK)
#     except Participant.DoesNotExist:
#         return Response({"success": False, "message": "Invalid winner_id", "data": {}}, status=status.HTTP_404_NOT_FOUND)
@api_view(['POST'])
def set_verified_winner(request, fixture_id):
    try:
        fixture = Fixture.objects.get(id=fixture_id)
    except Fixture.DoesNotExist:
        print(f"Fixture with id {fixture_id} does not exist.")
        return Response({"success": False, "message": "Fixture not found", "data": {}}, status=status.HTTP_404_NOT_FOUND)

    winner_id = request.data.get("winner_id")
    if not winner_id:
        print("winner_id not provided in the request.")
        return Response({"success": False, "message": "winner_id not provided", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

    try:
        winner = Participant.objects.get(id=winner_id)
        print(f"Winner fetched successfully: {winner}")

        # Validate if the winner is part of the fixture
        if winner not in [fixture.participant1, fixture.participant2]:
            print(f"Winner {winner} is not part of fixture {fixture.id}.")
            return Response({"success": False, "message": "Winner not part of this fixture", "data": {}}, status=status.HTTP_400_BAD_REQUEST)

        fixture.verified_winner = winner
        fixture.is_verified = True
        fixture.save()

        print(f"Fixture {fixture.id} updated with verified winner.")

        # Get the tournament related to the fixture
        tournament = fixture.tournament

        # Determine winner and loser, and their respective scores
        if winner == fixture.participant1:
            winner_score = 3
            loser = fixture.participant2
        else:
            winner_score = 3
            loser = fixture.participant1

        loser_score = 0

        # Check if MatchScore for winner already exists
        if not MatchScore.objects.filter(tournament=tournament, participant=winner, round=fixture.round).exists():
            print(f"Creating MatchScore for winner: {winner}")
            MatchScore.objects.create(
                tournament=tournament,
                participant=winner,
                round=fixture.round,
                win=True,
                lose=False,
                score=winner_score
            )
        else:
            print(f"MatchScore for winner {winner} already exists, skipping creation.")

        # Check if MatchScore for loser already exists
        if not MatchScore.objects.filter(tournament=tournament, participant=loser, round=fixture.round).exists():
            print(f"Creating MatchScore for loser: {loser}")
            MatchScore.objects.create(
                tournament=tournament,
                participant=loser,
                round=fixture.round,
                win=False,
                lose=True,
                score=loser_score
            )
        else:
            print(f"MatchScore for loser {loser} already exists, skipping creation.")

        # Calculate ranks based on score (assuming higher score gets a higher rank)
        match_scores = MatchScore.objects.filter(tournament=tournament, round=fixture.round).order_by('-score')
        print(f"Match scores for rank calculation: {list(match_scores)}")

        # Assign ranks based on score
        rank = 1
        for match_score in match_scores:
            print(f"Assigning rank {rank} to participant {match_score.participant}.")
            match_score.rank = rank
            match_score.save()
            rank += 1

        # Return the updated fixture data
        data = FixtureSerializer(fixture).data
        print(f"Response data: {data}")
        return Response({"success": True, "message": "Verified winner set successfully and scores created", "data": data}, status=status.HTTP_200_OK)

    except Participant.DoesNotExist:
        print(f"Participant with id {winner_id} does not exist.")
        return Response({"success": False, "message": "Invalid winner_id", "data": {}}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def set_verified_winner_all(request):
    fixture_winners = request.data.get("fixture_winners")

    print(f"Received fixture_winners: {fixture_winners}")

    if not fixture_winners or not isinstance(fixture_winners, list):
        return Response({"success": False, "message": "fixture_winners must be provided as a list of objects", "data": {}},
                        status=status.HTTP_400_BAD_REQUEST)

    updated_fixtures_data = []
    not_found_fixtures = []
    invalid_winners = []

    for item in fixture_winners:
        fixture_id = item.get("fixture_id")
        winner_id = item.get("winner_id")

        print(f"Processing fixture ID: {fixture_id}, winner ID: {winner_id}")

        if fixture_id is None or winner_id is None:
            return Response({"success": False, "message": "Both fixture_id and winner_id must be provided for each item", "data": {}},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the winner and fixture
            winner = Participant.objects.get(id=winner_id)
            print(f"Winner found: {winner}")

            fixture = Fixture.objects.get(id=fixture_id)
            print(f"Fixture found: {fixture}, Participant1: {fixture.participant1}, Participant2: {fixture.participant2}")

            # Determine the loser based on fixture participants
            if fixture.participant1 == winner:
                loser = fixture.participant2
                print(f"Loser identified as: {loser} (fixture.participant2)")
            elif fixture.participant2 == winner:
                loser = fixture.participant1
                print(f"Loser identified as: {loser} (fixture.participant1)")
            else:
                print(f"Error: Winner ID {winner_id} is not part of fixture {fixture_id}")
                return Response({"success": False, "message": f"Winner ID {winner_id} is not part of fixture {fixture_id}."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Get the round number from the fixture
            round_number = fixture.round_number
            print(f"Round number: {round_number}")

            # Update fixture to set the verified winner
            fixture.verified_winner = winner
            fixture.is_verified = True
            fixture.save()
            print(f"Fixture updated with verified winner: {fixture.verified_winner}")

            # Update or create MatchScore for the winner
            winner_score, created = MatchScore.objects.get_or_create(
                participant=winner,
                tournament=fixture.tournament,
                round=round_number  # Add round to the match score
            )
            winner_score.score += 3  # Add 3 points for winner
            winner_score.win = True
            winner_score.lose = False
            winner_score.save()
            print(f"Winner score updated: {winner_score}")

            # Update or create MatchScore for the loser
            if loser:
                loser_score, created = MatchScore.objects.get_or_create(
                    participant=loser,
                    tournament=fixture.tournament,
                    round=round_number  # Add round to the match score
                )
                loser_score.score = 0  # Loser gets 0 points
                loser_score.win = False
                loser_score.lose = True
                loser_score.save()
                print(f"Loser score updated: {loser_score}")
            else:
                print("No loser found to update score.")

            # Add fixture data to the response
            updated_fixtures_data.append(FixtureSerializer(fixture).data)

        except Fixture.DoesNotExist:
            not_found_fixtures.append(fixture_id)
            print(f"Fixture ID {fixture_id} not found")
        except Participant.DoesNotExist:
            invalid_winners.append(winner_id)
            print(f"Participant ID {winner_id} not found")

    # Construct response message
    success_message = "Verified winners set successfully for the following fixtures:"
    if updated_fixtures_data:
        success_message += f" {', '.join(str(f['id']) for f in updated_fixtures_data)}."
    if not_found_fixtures:
        success_message += f" The following fixture IDs were not found: {', '.join(map(str, not_found_fixtures))}."
    if invalid_winners:
        success_message += f" The following winner IDs were invalid: {', '.join(map(str, invalid_winners))}."

    print(f"Response message: {success_message}")

    return Response({
        "success": True,
        "message": success_message,
        "data": updated_fixtures_data
    }, status=status.HTTP_200_OK)



# class FixtureViewSet(viewsets.ModelViewSet):
#     queryset = Fixture.objects.all()
#     serializer_class = FixtureSerializer

#     @action(detail=True, methods=['post'], url_path='manage_fixtures')
#     def manage_fixtures(self, request, pk=None):
#         """
#         API to create fixtures for round 1 or advance to the next round based on existing fixtures.
#         """
#         tournament_id = pk  # Get the tournament ID from the URL

#         try:
#             tournament = Tournament.objects.get(id=tournament_id)
#             # Check if any fixtures exist; if not, create round 1
#             existing_fixtures = Fixture.objects.filter(tournament=tournament).order_by('-round_number')

#             if not existing_fixtures:
#                 # Create Round 1 fixtures
#                 participants = list(Participant.objects.filter(tournament=tournament))
#                 num_participants = len(participants)

#                 if num_participants < 2:
#                     return Response({
#                         'success': False,
#                         'message': 'At least two participants are required to create fixtures.'
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 fixtures = []
#                 match_date = datetime.combine(tournament.event_date, datetime.min.time())
#                 match_date = timezone.make_aware(match_date)

#                 if num_participants % 2 != 0:
#                     bye_participant = random.choice(participants)
#                     participants.remove(bye_participant)

#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=bye_participant,
#                         participant2=None,
#                         round_number=1,
#                         match_date=match_date,
#                         nominated_winner=bye_participant,
#                         verified_winner=bye_participant,
#                         is_verified=True
#                     )
#                     fixtures.append(fixture)

#                 for i in range(0, len(participants), 2):
#                     if i + 1 < len(participants):
#                         fixture = Fixture.objects.create(
#                             tournament=tournament,
#                             participant1=participants[i],
#                             participant2=participants[i + 1],
#                             round_number=1,
#                             match_date=match_date
#                         )
#                         fixtures.append(fixture)

#                 serializer = FixtureSerializer(fixtures, many=True)
#                 return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#             # Advance to the next round if fixtures exist
#             last_round = existing_fixtures.first().round_number
#             last_round_fixtures = Fixture.objects.filter(tournament=tournament, round_number=last_round, is_verified=True)

#             # Check if all fixtures in the last round are verified
#             if len(last_round_fixtures) != Fixture.objects.filter(tournament=tournament, round_number=last_round).count():
#                 return Response({
#                     'success': False,
#                     'message': 'Not all matches in the current round are verified. Complete the round first.'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             winners = [fixture.verified_winner for fixture in last_round_fixtures if fixture.verified_winner]
#             if len(winners) == 1:
#                 # Declare the last remaining participant as the tournament winner
#                 winner = winners[0]
#                 return Response({
#                     'success': True,
#                     'message': f'Tournament is complete. {winner.user.username} is the winner!'
#                 }, status=status.HTTP_200_OK)

#             if len(winners) < 2:
#                 return Response({
#                     'success': False,
#                     'message': 'No further rounds are needed.'
#                 }, status=status.HTTP_200_OK)

#             # Set match date for the new round
#             match_date = datetime.combine(tournament.event_date, datetime.min.time())
#             match_date = timezone.make_aware(match_date)
#             new_round = last_round + 1
#             fixtures = []

#             # If odd number of winners, give a bye
#             if len(winners) % 2 != 0:
#                 bye_participant = random.choice(winners)
#                 winners.remove(bye_participant)

#                 fixture = Fixture.objects.create(
#                     tournament=tournament,
#                     participant1=bye_participant,
#                     participant2=None,
#                     round_number=new_round,
#                     match_date=match_date,
#                     nominated_winner=bye_participant,
#                     verified_winner=bye_participant,
#                     is_verified=True
#                 )
#                 fixtures.append(fixture)

#             # Create fixtures for the new round
#             for i in range(0, len(winners), 2):
#                 if i + 1 < len(winners):
#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=winners[i],
#                         participant2=winners[i + 1],
#                         round_number=new_round,
#                         match_date=match_date
#                     )
#                     fixtures.append(fixture)

#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#         except Tournament.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Tournament not found.'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
db = firestore.client()
class FixtureViewSet(viewsets.ModelViewSet):
    queryset = Fixture.objects.all()
    serializer_class = FixtureSerializer

    @action(detail=True, methods=['post'], url_path='manage_fixtures')
    def manage_fixtures(self, request, pk=None):
        """
        API to create fixtures for round 1 or advance to the next round based on existing fixtures.
        Only participants who have arrived_at_venue=True will be included in the fixtures.
        """
        tournament_id = pk  # Get the tournament ID from the URL

        try:
            tournament = Tournament.objects.get(id=tournament_id)
            # Fetch fixtures for the tournament, ordered by round number
            existing_fixtures = Fixture.objects.filter(tournament=tournament).order_by('-round_number')

            if not existing_fixtures:
                # Create Round 1 fixtures if no fixtures exist
                participants = list(Participant.objects.filter(tournament=tournament, arrived_at_venue=True))
                num_participants = len(participants)

                if num_participants < 2:
                    return Response({
                        'success': False,
                        'message': 'At least two participants who have arrived at the venue are required to create fixtures.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                fixtures = []
                match_date = timezone.make_aware(datetime.combine(tournament.event_date, datetime.min.time()))

                # Handle bye if participants are odd
                if num_participants % 2 != 0:
                    bye_participant = random.choice(participants)
                    participants.remove(bye_participant)
                    fixture = Fixture.objects.create(
                        tournament=tournament,
                        participant1=bye_participant,
                        participant2=None,
                        round_number=1,
                        match_date=match_date,
                        nominated_winner=bye_participant,
                        verified_winner=bye_participant,
                        is_verified=True
                    )
                    fixtures.append(fixture)
                    self.create_firestore_record(fixture)  # Added Firestore record creation

                # Create match fixtures for Round 1
                for i in range(0, len(participants), 2):
                    if i + 1 < len(participants):
                        fixture = Fixture.objects.create(
                            tournament=tournament,
                            participant1=participants[i],
                            participant2=participants[i + 1],
                            round_number=1,
                            match_date=match_date
                        )
                        fixtures.append(fixture)
                        self.create_firestore_record(fixture)  # Added Firestore record creation

                serializer = FixtureSerializer(fixtures, many=True)
                return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

            # Determine the last completed round
            last_round = existing_fixtures.first().round_number
            last_round_fixtures = Fixture.objects.filter(
                tournament=tournament,
                round_number=last_round,
                is_verified=True
            )

            # Ensure all matches in the last round are verified
            if len(last_round_fixtures) != Fixture.objects.filter(tournament=tournament, round_number=last_round).count():
                return Response({
                    'success': False,
                    'message': 'Not all matches in the current round are verified. Complete the round first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Collect winners from the last round
            winners = [fixture.verified_winner for fixture in last_round_fixtures if fixture.verified_winner and fixture.verified_winner.arrived_at_venue]

            if len(winners) == 1:
                # If only one winner remains, they win the tournament
                winner = winners[0]
                winner_data = ParticipantSerializerforfixture(winner).data
                tournament.is_active = False
                tournament.save()
                return Response({
                    'success': True,
                    'message': f'Tournament is complete. {winner.user.username} is the winner!',
                    'winner_data': winner_data
                }, status=status.HTTP_200_OK)

            if len(winners) < 2:
                # No further rounds are necessary if fewer than two winners
                return Response({
                    'success': False,
                    'message': 'No further rounds are needed.'
                }, status=status.HTTP_200_OK)

            # Set match date and advance to the next round
            match_date = timezone.make_aware(datetime.combine(tournament.event_date, datetime.min.time()))
            new_round = last_round + 1
            fixtures = []

            # Handle odd number of winners by giving a bye
            if len(winners) % 2 != 0:
                bye_participant = random.choice(winners)
                winners.remove(bye_participant)
                fixture = Fixture.objects.create(
                    tournament=tournament,
                    participant1=bye_participant,
                    participant2=None,
                    round_number=new_round,
                    match_date=match_date,
                    nominated_winner=bye_participant,
                    verified_winner=bye_participant,
                    is_verified=True
                )
                fixtures.append(fixture)
                self.create_firestore_record(fixture)  # Added Firestore record creation

            # Create fixtures for the new round
            for i in range(0, len(winners), 2):
                if i + 1 < len(winners):
                    fixture = Fixture.objects.create(
                        tournament=tournament,
                        participant1=winners[i],
                        participant2=winners[i + 1],
                        round_number=new_round,
                        match_date=match_date
                    )
                    fixtures.append(fixture)
                    self.create_firestore_record(fixture)  # Added Firestore record creation

            serializer = FixtureSerializer(fixtures, many=True)
            return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

        except Tournament.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Tournament not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_firestore_record(self, fixture):
        # Create a Firestore document in the "tournaments" collection for the given fixture
            tournament_name = fixture.tournament.tournament_name
            round_number = fixture.round_number

            # Prepare participant1 data
            participant1_data = {
                "id": fixture.participant1.id if fixture.participant1 else None,
                "user": {
                    "contact": fixture.participant1.user.contact if fixture.participant1 else None,
                    "id": fixture.participant1.user.id if fixture.participant1 else None,
                    "email": fixture.participant1.user.email if fixture.participant1 else None,
                    "username": fixture.participant1.user.username if fixture.participant1 else None,
                    "user_type": fixture.participant1.user.user_type if fixture.participant1 else None,
                    "is_active": fixture.participant1.user.is_active if fixture.participant1 else None,
                    "is_admin": fixture.participant1.user.is_admin if fixture.participant1 else None,
                    "created_at": fixture.participant1.user.created_at.isoformat() if fixture.participant1 else None,
                    "updated_at": fixture.participant1.user.updated_at.isoformat() if fixture.participant1 else None,
                    "image": fixture.participant1.user.image.url if fixture.participant1 and fixture.participant1.user.image else None,
                    "is_registered": fixture.participant1.user.is_registered if fixture.participant1 else None,
                    "is_deleted": fixture.participant1.user.is_deleted if fixture.participant1 else None,
                    "full_name": fixture.participant1.user.full_name if fixture.participant1 else None,
                    "address": fixture.participant1.user.address if fixture.participant1 else None,
                    "longitude": fixture.participant1.user.longitude if fixture.participant1 else None,
                    "latitude": fixture.participant1.user.latitude if fixture.participant1 else None,
                },
                "tournament": fixture.participant1.tournament.id if fixture.participant1 else None,
                "tournament_name": fixture.participant1.tournament.tournament_name if fixture.participant1 else None,
                "deck_name": fixture.participant1.deck.name if fixture.participant1 else None,
                "registration_date": fixture.participant1.registration_date.isoformat() if fixture.participant1 else None,
                "payment_status": fixture.participant1.payment_status if fixture.participant1 else None,
                "total_score": fixture.participant1.total_score if fixture.participant1 else None,
                "is_ready": fixture.participant1.is_ready if fixture.participant1 else None
            } if fixture.participant1 else None

            # Prepare participant2 data (similar to participant1)
            participant2_data = {
                "id": fixture.participant2.id if fixture.participant2 else None,
                "user": {
                    "contact": fixture.participant2.user.contact if fixture.participant2 else None,
                    "id": fixture.participant2.user.id if fixture.participant2 else None,
                    "email": fixture.participant2.user.email if fixture.participant2 else None,
                    "username": fixture.participant2.user.username if fixture.participant2 else None,
                    "user_type": fixture.participant2.user.user_type if fixture.participant2 else None,
                    "is_active": fixture.participant2.user.is_active if fixture.participant2 else None,
                    "is_admin": fixture.participant2.user.is_admin if fixture.participant2 else None,
                    "created_at": fixture.participant2.user.created_at.isoformat() if fixture.participant2 else None,
                    "updated_at": fixture.participant2.user.updated_at.isoformat() if fixture.participant2 else None,
                    "image": fixture.participant2.user.image.url if fixture.participant2 and fixture.participant2.user.image else None,
                    "is_registered": fixture.participant2.user.is_registered if fixture.participant2 else None,
                    "is_deleted": fixture.participant2.user.is_deleted if fixture.participant2 else None,
                    "full_name": fixture.participant2.user.full_name if fixture.participant2 else None,
                    "address": fixture.participant2.user.address if fixture.participant2 else None,
                    "longitude": fixture.participant2.user.longitude if fixture.participant2 else None,
                    "latitude": fixture.participant2.user.latitude if fixture.participant2 else None,
                },
                "tournament": fixture.participant2.tournament.id if fixture.participant2 else None,
                "tournament_name": fixture.participant2.tournament.tournament_name if fixture.participant2 else None,
                "deck_name": fixture.participant2.deck.name if fixture.participant2 else None,
                "registration_date": fixture.participant2.registration_date.isoformat() if fixture.participant2 else None,
                "payment_status": fixture.participant2.payment_status if fixture.participant2 else None,
                "total_score": fixture.participant2.total_score if fixture.participant2 else None,
                "is_ready": fixture.participant2.is_ready if fixture.participant2 else None
            } if fixture.participant2 else None

            # Create the match data dictionary
            match_data = {
                "id": fixture.id,
                "tournament": fixture.tournament.id,
                "participant1": participant1_data,
                "participant2": participant2_data,
                "round_number": round_number,
                "match_date": fixture.match_date.isoformat(),
                "nominated_winner": fixture.nominated_winner.id if fixture.nominated_winner else None,
                "verified_winner": fixture.verified_winner.id if fixture.verified_winner else None,
                "is_verified": fixture.is_verified,
                "start_time": fixture.start_time if hasattr(fixture, 'start_time') else None,  # Ensure `start_time` exists
                "is_tournament_completed": fixture.is_tournament_completed
            }

            print(f"Creating Firestore record for fixture: {match_data}")

            tournament_ref = db.collection(tournament_name).add(match_data)


# class FixtureViewSet(viewsets.ModelViewSet):
#     queryset = Fixture.objects.all()
#     serializer_class = FixtureSerializer

#     @action(detail=True, methods=['post'], url_path='manage_fixtures')
#     def manage_fixtures(self, request, pk=None):
#         """
#         API to create fixtures for round 1 or advance to the next round based on existing fixtures.
#         """
#         tournament_id = pk  # Get the tournament ID from the URL

#         try:
#             tournament = Tournament.objects.get(id=tournament_id)
#             # Fetch fixtures for the tournament, ordered by round number
#             existing_fixtures = Fixture.objects.filter(tournament=tournament).order_by('-round_number')

#             if not existing_fixtures:
#                 # Create Round 1 fixtures if no fixtures exist
#                 participants = list(Participant.objects.filter(tournament=tournament))
#                 num_participants = len(participants)

#                 if num_participants < 2:
#                     return Response({
#                         'success': False,
#                         'message': 'At least two participants are required to create fixtures.'
#                     }, status=status.HTTP_400_BAD_REQUEST)

#                 fixtures = []
#                 match_date = timezone.make_aware(datetime.combine(tournament.event_date, datetime.min.time()))

#                 # Handle bye if participants are odd
#                 if num_participants % 2 != 0:
#                     bye_participant = random.choice(participants)
#                     participants.remove(bye_participant)
#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=bye_participant,
#                         participant2=None,
#                         round_number=1,
#                         match_date=match_date,
#                         nominated_winner=bye_participant,
#                         verified_winner=bye_participant,
#                         is_verified=True
#                     )
#                     fixtures.append(fixture)

#                 # Create match fixtures for Round 1
#                 for i in range(0, len(participants), 2):
#                     if i + 1 < len(participants):
#                         fixture = Fixture.objects.create(
#                             tournament=tournament,
#                             participant1=participants[i],
#                             participant2=participants[i + 1],
#                             round_number=1,
#                             match_date=match_date
#                         )
#                         fixtures.append(fixture)

#                 serializer = FixtureSerializer(fixtures, many=True)
#                 return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#             # Determine the last completed round
#             last_round = existing_fixtures.first().round_number
#             last_round_fixtures = Fixture.objects.filter(
#                 tournament=tournament,
#                 round_number=last_round,
#                 is_verified=True
#             )

#             # Ensure all matches in the last round are verified
#             if len(last_round_fixtures) != Fixture.objects.filter(tournament=tournament, round_number=last_round).count():
#                 return Response({
#                     'success': False,
#                     'message': 'Not all matches in the current round are verified. Complete the round first.'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Collect winners from the last round
#             winners = [fixture.verified_winner for fixture in last_round_fixtures if fixture.verified_winner]

#             if len(winners) == 1:
#                 # If only one winner remains, they win the tournament
#                 winner = winners[0]
#                 winner_data = ParticipantSerializerforfixture(winner).data
#                 return Response({
#                     'success': True,
#                     'message': f'Tournament is complete. {winner.user.username} is the winner!',
#                     'winner_data': winner_data
#                 }, status=status.HTTP_200_OK)

#             if len(winners) < 2:
#                 # No further rounds are necessary if fewer than two winners
#                 return Response({
#                     'success': False,
#                     'message': 'No further rounds are needed.'
#                 }, status=status.HTTP_200_OK)

#             # Set match date and advance to the next round
#             match_date = timezone.make_aware(datetime.combine(tournament.event_date, datetime.min.time()))
#             new_round = last_round + 1
#             fixtures = []

#             # Handle odd number of winners by giving a bye
#             if len(winners) % 2 != 0:
#                 bye_participant = random.choice(winners)
#                 winners.remove(bye_participant)
#                 fixture = Fixture.objects.create(
#                     tournament=tournament,
#                     participant1=bye_participant,
#                     participant2=None,
#                     round_number=new_round,
#                     match_date=match_date,
#                     nominated_winner=bye_participant,
#                     verified_winner=bye_participant,
#                     is_verified=True
#                 )
#                 fixtures.append(fixture)

#             # Create fixtures for the new round
#             for i in range(0, len(winners), 2):
#                 if i + 1 < len(winners):
#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=winners[i],
#                         participant2=winners[i + 1],
#                         round_number=new_round,
#                         match_date=match_date
#                     )
#                     fixtures.append(fixture)

#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#         except Tournament.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Tournament not found.'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class admingetallTournamentFixturesView(APIView):
#     def get(self, request, tournament_id):
#         try:
#             # Check if tournament exists
#             tournament = Tournament.objects.get(id=tournament_id)

#             # Get all fixtures for the tournament
#             fixtures = Fixture.objects.filter(tournament=tournament)

#             # Serialize the fixtures
#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({
#                 "success": True,
#                 "message": "Fixtures retrieved successfully.",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Tournament.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "Tournament not found."
#             }, status=status.HTTP_404_NOT_FOUND)
class UserTournamentFixturesView(generics.ListAPIView):
    serializer_class = FixtureSerializer

    def get_queryset(self):
        tournament_id = self.kwargs['tournament_id']
        user_id = self.kwargs['user_id']

        # Filter fixtures where the user is either participant1 or participant2 in the specified tournament
        return Fixture.objects.filter(
            tournament__id=tournament_id
        ).filter(
            participant1__user__id=user_id
        ) | Fixture.objects.filter(
            tournament__id=tournament_id
        ).filter(
            participant2__user__id=user_id
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({
                "success": False,
                "message": "No fixtures found for the specified tournament and user.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "User fixtures retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

# class FixtureViewSet(viewsets.ModelViewSet):
#     queryset = Fixture.objects.all()
#     serializer_class = FixtureSerializer

#     @action(detail=True, methods=['post'], url_path='create_round_1_fixtures')
#     def create_round_1_fixtures(self, request, pk=None):
#         """
#         API to create fixtures for round 1 of a tournament.
#         """
#         tournament_id = pk  # Get the tournament ID from the URL

#         try:
#             tournament = Tournament.objects.get(id=tournament_id)
#             participants = list(Participant.objects.filter(tournament=tournament))

#             num_participants = len(participants)
#             if num_participants < 2:
#                 return Response({
#                     'success': False,
#                     'message': 'At least two participants are required to create fixtures.'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             fixtures = []
#             match_date = datetime.combine(tournament.event_date, datetime.min.time())
#             match_date = timezone.make_aware(match_date)

#             if num_participants % 2 != 0:
#                 bye_participant = random.choice(participants)
#                 participants.remove(bye_participant)

#                 fixture = Fixture.objects.create(
#                     tournament=tournament,
#                     participant1=bye_participant,
#                     participant2=None,
#                     round_number=1,
#                     match_date=match_date,
#                     nominated_winner=bye_participant,
#                     verified_winner=bye_participant,
#                     is_verified=True
#                 )
#                 fixtures.append(fixture)

#             for i in range(0, len(participants), 2):
#                 if i + 1 < len(participants):
#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=participants[i],
#                         participant2=participants[i + 1],
#                         round_number=1,
#                         match_date=match_date
#                     )
#                     fixtures.append(fixture)

#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#         except Tournament.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Tournament not found.'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @action(detail=True, methods=['post'], url_path='advance_to_next_round')
#     def advance_to_next_round(self, request, pk=None):
#         """
#         API to create fixtures for the next round based on the winners of the previous round.
#         """
#         tournament_id = pk

#         try:
#             tournament = Tournament.objects.get(id=tournament_id)
#             last_round = Fixture.objects.filter(tournament=tournament).order_by('-round_number').first().round_number

#             # Check if all fixtures in the last round are verified
#             last_round_fixtures = Fixture.objects.filter(tournament=tournament, round_number=last_round, is_verified=True)
#             if len(last_round_fixtures) != Fixture.objects.filter(tournament=tournament, round_number=last_round).count():
#                 return Response({
#                     'success': False,
#                     'message': 'Not all matches in the current round are verified. Complete the round first.'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             winners = [fixture.verified_winner for fixture in last_round_fixtures if fixture.verified_winner]
#             if len(winners) == 1:
#                 # Declare the last remaining participant as the tournament winner
#                 winner = winners[0]
#                 return Response({
#                     'success': True,
#                     'message': f'Tournament is complete. {winner.user.username} is the winner!'
#                 }, status=status.HTTP_200_OK)

#             if len(winners) < 2:
#                 return Response({
#                     'success': False,
#                     'message': 'No further rounds are needed.'
#                 }, status=status.HTTP_200_OK)

#             # Set match date for the new round
#             match_date = datetime.combine(tournament.event_date, datetime.min.time())
#             match_date = timezone.make_aware(match_date)
#             new_round = last_round + 1
#             fixtures = []

#             # If odd number of winners, give a bye
#             if len(winners) % 2 != 0:
#                 bye_participant = random.choice(winners)
#                 winners.remove(bye_participant)

#                 fixture = Fixture.objects.create(
#                     tournament=tournament,
#                     participant1=bye_participant,
#                     participant2=None,
#                     round_number=new_round,
#                     match_date=match_date,
#                     nominated_winner=bye_participant,
#                     verified_winner=bye_participant,
#                     is_verified=True
#                 )
#                 fixtures.append(fixture)

#             # Create fixtures for the new round
#             for i in range(0, len(winners), 2):
#                 if i + 1 < len(winners):
#                     fixture = Fixture.objects.create(
#                         tournament=tournament,
#                         participant1=winners[i],
#                         participant2=winners[i + 1],
#                         round_number=new_round,
#                         match_date=match_date
#                     )
#                     fixtures.append(fixture)

#             serializer = FixtureSerializer(fixtures, many=True)
#             return Response({'success': True, 'fixtures': serializer.data}, status=status.HTTP_201_CREATED)

#         except Tournament.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Tournament not found.'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 'success': False,
#                 'message': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class UserGameDecksViewnew(generics.ListAPIView):
    serializer_class = DeckSerializerfordeck

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        game_id = self.kwargs['game_id']
        return Deck.objects.filter(user_id=user_id, game_id=game_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Decks retrieved successfully.",
            "data": serializer.data
        })
class UserGameDecksView(generics.ListAPIView):
    serializer_class = DeckSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        game_id = self.kwargs['game_id']
        return Deck.objects.filter(user_id=user_id, game_id=game_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Decks retrieved successfully.",
            "data": serializer.data
        })
class AddMultipleCardsView(APIView):
    def post(self, request, deck_id):
        # Ensure the specified deck exists
        deck = get_object_or_404(Deck, id=deck_id)

        # Add deck_id to each card entry in the request data
        cards_data = request.data
        for card_data in cards_data:
            card_data['deck'] = deck.id  # Assign the deck_id to each card

        # Serialize and save the data
        serializer = CardSerializer(data=cards_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Cards created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Failed to create cards.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def fetch_cards(request):
    url = "https://api.magicthegathering.io/v1/cards"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        formatted_cards = []

        # Loop through the cards and format them
        for card in data.get('cards', []):
            formatted_card = {
                "ID": card.get('id'),
                "Title": card.get('name'),
                "Price": card.get('prices', {}).get('usd', None),  # Adjust based on the actual API structure
                "Color": ', '.join(card.get('colors', [])),
                "Source": card.get('set', 'Unknown'),
                "CardType": card.get('type'),
                "Power": card.get('power', 'N/A'),  # Adjust based on the actual API structure
                "Effect": card.get('text', 'N/A'),
                "Images": card.get('imageUrl', '')
            }
            formatted_cards.append(formatted_card)

        return JsonResponse(formatted_cards, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch data from Magic: The Gathering API"}, status=response.status_code)

class PokemonCardsView(APIView):
    def get(self, request):
        url = "https://api.pokemontcg.io/v2/cards"

        try:
            # Fetch the data from the external API
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()
            cards = data.get('data', [])

            # Process each card to extract required details
            formatted_cards = []
            for card in cards:
                formatted_card = {
                    "ID": card.get("id"),
                    "Title": card.get("name"),
                    "Price": card.get("cardmarket", {}).get("prices", {}).get("averageSellPrice"),  # Directly set the price
                    "Color": card.get("types", [])[0] if card.get("types") else None,
                    "Source": card.get("set", {}).get("name"),
                    "CardType": card.get("supertype"),
                    "Power": card.get("hp"),  # Get the ability name
                    "Effect": card.get("attacks", [{}])[0].get("name") if card.get("attacks") else None,  # Attack name as Effect
                    "Images":  card.get("images", {}).get("small"),
                    "Quantity":0
                }
                formatted_cards.append(formatted_card)

            # Build the response structure
            response_data = {
                "success": True,
                "message": "Cards retrieved successfully",
                "data": formatted_cards
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
class DeckCreateView(APIView):
    def post(self, request):
        data = request.data.copy()
        print("Received data:", data)  # Debug print to check incoming request data

        # Retrieve and validate user ID from the request data
        user_id = data.get("user")
        print("User ID from request:", user_id)  # Print user ID for debugging

        if not user_id:
            print("User ID is missing in the request.")  # Notify missing user ID
            return Response({
                "success": False,
                "message": "User ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            print("User found:", user)  # Confirm user retrieval
        except User.DoesNotExist:
            print("User not found for ID:", user_id)  # Notify if user is not found
            return Response({
                "success": False,
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        data['user'] = user.id  # Set the user field in data
        print("Data after setting user:", data)  # Debug print to check modified data

        # Proceed with creating the Deck instance
        serializer = DeckSerializercreate(data=data)
        if serializer.is_valid():
            deck = serializer.save()
            print("Deck created successfully:", deck)  # Confirm deck creation
            return Response({
                "success": True,
                "message": "Deck created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        print("Serializer errors:", serializer.errors)  # Print serializer errors for debugging
        return Response({
            "success": False,
            "message": "Failed to create deck.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
class UserParticipantsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            participants = Participant.objects.filter(user=user)
            serializer = ParticipantSerializernew(participants, many=True)
            return Response({
                "success": True,
                "message": "Participants retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)






class TournamentByGameView(APIView):
    def get(self, request, game_id):
        # Filter tournaments based on the provided game_id
        active_tournaments = Tournament.objects.filter(game_id=game_id)

        # Initialize the list to hold tournament data
        tournaments_data = []

        for tournament in active_tournaments:
            # Filter participants who have paid and are not disqualified
            paid_participants = Participant.objects.filter(
                tournament=tournament, payment_status='paid', is_disqualified=False
            ).select_related('user')

            # Filter participants who are disqualified
            disqualified_participants = Participant.objects.filter(
                tournament=tournament, is_disqualified=True
            ).select_related('user')

            # Serialize the tournament data
            tournament_data = TournamentSerializernew(tournament).data

            # Append the paid participants data
            tournament_data['paid_participants'] = ParticipantSerializer(paid_participants, many=True).data




            # Add the tournament data to the list
            tournaments_data.append(tournament_data)

        # Construct the response
        return Response({
            'success': True,
            'message': 'Tournaments retrieved successfully.',
            'data': tournaments_data
        }, status=status.HTTP_200_OK)
@api_view(['POST'])
def create_banner_image(request):
    serializer = newBannerImageSerializer(data=request.data)
    if serializer.is_valid():
        banner_image = serializer.save()
        return Response({
            'success': True,
            'message': 'Banner image uploaded successfully.',
            'data': BannerImageSerializer(banner_image).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'message': 'Failed to upload banner image.',
        'data': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def create_featured_tournament(request):
    print("Received request data:", request.data)  # Print incoming request data

    tournament_id = request.data.get('tournament')
    print("Extracted tournament ID:", tournament_id)  # Print extracted tournament ID

    if tournament_id is None:
        print("Tournament ID is missing.")  # Print if tournament ID is missing
        return Response({
            'success': False,
            'message': 'Tournament ID is required.',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        tournament = Tournament.objects.get(id=tournament_id)
        print("Tournament found:", tournament)  # Print found tournament

        # Check if the tournament is already featured
        if FeaturedTournament.objects.filter(tournament=tournament).exists():
            print("This tournament is already featured.")  # Print if it already exists
            return Response({
                'success': False,
                'message': 'This tournament is already featured.',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

    except Tournament.DoesNotExist:
        print(f"Tournament with id {tournament_id} does not exist.")  # Print error message
        return Response({
            'success': False,
            'message': f'Tournament with id {tournament_id} does not exist.',
            'data': {}
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create FeaturedTournament object
    featured_tournament = FeaturedTournament(
        tournament=tournament,
        is_featured=request.data.get('is_featured', False),
        featured_date=request.data.get('featured_date'),
    )

    try:
        featured_tournament.save()  # Save the object
        print("Featured tournament created successfully:", featured_tournament)  # Print success message
        return Response({
            'success': True,
            'message': 'Featured tournament created successfully.',
            'data': createFeaturedTournamentSerializer(featured_tournament).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Error occurred while creating featured tournament:", str(e))  # Print error message
        return Response({
            'success': False,
            'message': 'Failed to create featured tournament.',
            'data': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class GameListView(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def get(self, request, *args, **kwargs):
        games = self.get_queryset()
        serializer = self.get_serializer(games, many=True)
        return api_response(success=True, message="Games retrieved successfully", data=serializer.data)
class TournamentListView(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = getTournamentSerializer

class TournamentCreateView(generics.CreateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return api_response(
                success=True,
                message="Tournament created successfully",
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return api_response(
                success=False,
                message="Failed to create tournament",
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
class TournamentListView(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Tournaments retrieved successfully",
            data=serializer.data
        )

class RegisterForTournamentView(generics.CreateAPIView):
    serializer_class = ParticipantSerializer

    def create(self, request, *args, **kwargs):
        tournament_id = self.kwargs.get('tournament_id')
        tournament = get_object_or_404(Tournament, id=tournament_id)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            participant = serializer.save(user=request.user, tournament=tournament)
            return api_response(True, 'Successfully registered for the tournament.', ParticipantSerializer(participant).data)

        return api_response(False, 'Registration failed.', serializer.errors)

# API for creating a score for a participant
# class ScoreCreateView(generics.CreateAPIView):
#     serializer_class = ScoreSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             score = serializer.save()
#             return api_response(True, 'Score created successfully.', ScoreSerializer(score).data)

#         return api_response(False, 'Failed to create score.', serializer.errors)
@api_view(['GET'])
def featured_tournament_list(request):
    featured_tournaments = FeaturedTournament.objects.all()
    if featured_tournaments.exists():
        serializer = FeaturedTournamentSerializer(featured_tournaments, many=True)
        return Response({
            'success': True,
            'message': 'Featured tournaments retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'No featured tournaments found.',
            'data': []
        }, status=status.HTTP_200_OK)

# Function-based view for retrieving a specific featured tournament by id
@api_view(['GET'])
def featured_tournament_detail(request, pk):
    try:
        featured_tournament = FeaturedTournament.objects.get(pk=pk)
        serializer = FeaturedTournamentSerializer(featured_tournament)
        return Response({
            'success': True,
            'message': 'Featured tournament retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except FeaturedTournament.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Featured tournament not found.',
            'data': {}
        }, status=status.HTTP_404_NOT_FOUND)

# Function-based view for listing all banner images
@api_view(['GET'])
def banner_image_list(request):
    # Filter BannerImage objects where status is True
    banner_images = BannerImage.objects.filter(tournament__is_active=True)

    if banner_images.exists():
        serializer = BannerImageSerializer(banner_images, many=True)
        return Response({
            'success': True,
            'message': 'Banner images retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'No banner images found.',
            'data': []
        }, status=status.HTTP_200_OK)

# Function-based view for retrieving a specific banner image by id
@api_view(['GET'])
def banner_image_detail(request, pk):
    try:
        banner_image = BannerImage.objects.get(pk=pk)
        serializer = BannerImageSerializer(banner_image)
        return Response({
            'success': True,
            'message': 'Banner image retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except BannerImage.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Banner image not found.',
            'data': {}
        }, status=status.HTTP_404_NOT_FOUND)



# views.py






@api_view(['POST'])
def register_for_tournament(request, user_id):
    tournament_id = request.data.get('tournament')  # Get tournament ID from the request
    deck_id = request.data.get('deck')  # Get deck ID from the request

    # Check if the tournament and deck exist
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        deck = Deck.objects.get(id=deck_id)
    except (Tournament.DoesNotExist, Deck.DoesNotExist) as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the participant already exists
    existing_participant = Participant.objects.filter(user_id=user_id, tournament=tournament).first()
    if existing_participant:
        return Response({
            "success": False,
            "message": "You are already registered for this tournament.",
            "data": ParticipantSerializer(existing_participant).data
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create the participant
    participant = Participant.objects.create(
        user_id=user_id,
        tournament=tournament,
        deck=deck,
        payment_status="paid",

    )

    # Serialize the participant to return the response
    serializer = ParticipantSerializer(participant)

    return Response({
        "success": True,
        "message": "Registration successful.",
        "data": serializer.data
    })


class TournamentViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        """API to retrieve a specific tournament."""
        tournament = self.get_tournament(pk)
        if tournament:
            serializer = TournamentSerializer(tournament)
            return Response({
                'success': True,
                'message': 'Tournament retrieved successfully.',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'message': 'Tournament not found.',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """API to update an existing tournament."""
        tournament = self.get_tournament(pk)
        if tournament:
            serializer = TournamentSerializer(tournament, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Tournament updated successfully.',
                    'data': serializer.data
                })
            return Response({
                'success': False,
                'message': 'Validation error.',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'message': 'Tournament not found.',
            'data': None
        }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])


    def save_draft(self, request, user_id):
        """API to save tournament as draft with user ID from URL."""

        # Get the user instance from the user_id provided in the URL
        user = get_object_or_404(User, pk=user_id)

        # Proceed with the serializer
        serializer = DraftTournamentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=user)  # Use the fetched user instance
            return Response({
                'success': True,
                'message': 'Draft tournament saved successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': 'Validation error.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def drafts(self, request, user_id):
        """API to get draft tournaments by user ID."""
        drafts = Tournament.objects.filter(created_by=user_id, is_draft=True)
        serializer = TournamentSerializernew(drafts, many=True)
        return Response({
            'success': True,
            'message': 'Draft tournaments retrieved successfully.',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """API to get all tournaments where is_draft is False along with paid participants and disqualified players."""
        active_tournaments = Tournament.objects.filter(is_draft=False).order_by('event_date')

        tournaments_data = []
        for tournament in active_tournaments:
            # Filter participants who have paid and are not disqualified
            paid_participants = Participant.objects.filter(
                tournament=tournament, payment_status='paid', is_disqualified=False
            ).select_related('user')

            # Filter participants who are disqualified
            disqualified_participants = Participant.objects.filter(
                tournament=tournament, is_disqualified=True
            ).select_related('user')

            tournament_data = TournamentSerializernew(tournament).data
            tournament_data['paid_participants'] = ParticipantSerializer(paid_participants, many=True).data
            tournament_data['disqualified_participants'] = ParticipantSerializer(disqualified_participants, many=True).data
            tournaments_data.append(tournament_data)

        return Response({
            'success': True,
            'message': 'Active tournaments retrieved successfully.',
            'data': tournaments_data
        }, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'])
    def all_tournaments(self, request):
        """API to get all tournaments where is_draft is False."""
        tournaments = Tournament.objects.filter(is_draft=False)

        # Serialize the tournament data
        tournament_data = TournamentSerializer(tournaments, many=True).data

        return Response({
            'success': True,
            'message': 'Tournaments retrieved successfully.',
            'data': tournament_data
        })
    @action(detail=False, methods=['post'], url_path='disqualify_user/(?P<user_id>[^/.]+)')
    def disqualify_user(self, request, tournament_id, user_id):
        """API to disqualify a user from a tournament."""
        try:
            # Find the participant
            participant = Participant.objects.get(tournament_id=tournament_id, user_id=user_id)
            participant.is_disqualified = True  # Set disqualified status
            participant.save()

            return Response({
                'success': True,
                'message': 'User disqualified successfully.',
                'data': ParticipantSerializer(participant).data
            }, status=status.HTTP_200_OK)

        except Participant.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Participant not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'])
    def convert_to_actual(self, request, pk=None):
        """API to convert draft tournament to actual tournament."""
        tournament = self.get_tournament(pk)
        if tournament and tournament.is_draft:
            tournament.is_draft = False
            tournament.save()
            serializer = TournamentSerializer(tournament)
            return Response({
                'success': True,
                'message': 'Draft tournament converted to actual successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'message': 'Tournament is not a draft or not found.',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['get'])
    def eligible_participants(self, request, pk=None):
        """
        API to get all participants of a specific tournament where:
        - payment_status is 'paid'
        - is_disqualified is False
        - arrived_at_venue is True
        """
        try:
            tournament = Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Tournament not found.'
            }, status=404)

        participants = Participant.objects.filter(
            tournament=tournament,
            payment_status='paid',
            is_disqualified=False
            # arrived_at_venue=True
        ).select_related('user')

        # Serialize participants
        participants_data = ParticipantSerializernewforactivelist(participants, many=True).data

        return Response({
            'success': True,
            'message': 'Eligible participants retrieved successfully.',
            'data': participants_data
        })
    @action(detail=True, methods=['get'])
    def Tournament_participants(self, request, pk=None):
        """
        API to get all participants of a specific tournament where:
        - payment_status is 'paid'
        - is_disqualified is False
        - arrived_at_venue is True
        """
        try:
            tournament = Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Tournament not found.'
            }, status=404)

        participants = Participant.objects.filter(
            tournament=tournament,
            payment_status='paid',
            is_disqualified=False,

        ).select_related('user')

        # Serialize participants
        participants_data = ParticipantSerializernewforactivelist(participants, many=True).data

        return Response({
            'success': True,
            'message': 'Eligible participants retrieved successfully.',
            'data': participants_data
        })
    @action(detail=True, methods=['put'])
    def update_draft(self, request, pk=None):
        """API to update draft tournament."""
        tournament = self.get_tournament(pk)
        if tournament and tournament.is_draft:
            serializer = DraftTournamentSerializer(tournament, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Draft tournament updated successfully.',
                    'data': serializer.data
                })
            return Response({
                'success': False,
                'message': 'Validation error.',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'message': 'Tournament is not a draft or not found.',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)

    def get_tournament(self, pk):
        """Helper method to retrieve a tournament instance."""
        try:
            return Tournament.objects.get(pk=pk)
        except Tournament.DoesNotExist:
            return None


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer

    @action(detail=False, methods=['patch'], url_path='arrive-at-venue')
    def arrive_at_venue(self, request):
        """
        API endpoint for updating the 'arrived_at_venue' field
        for a specific tournament without requiring authentication.
        """
        user_id = request.data.get('user_id')
        tournament_id = request.data.get('tournament_id')

        if not user_id or not tournament_id:
            return Response({'error': 'User ID and Tournament ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the participant record for the provided user and tournament ID
            participant = Participant.objects.get(user_id=user_id, tournament_id=tournament_id)
            participant.arrived_at_venue = True
            participant.save()

            return Response({
                'success': True,
                'message': 'Arrived at venue status updated successfully.',
                'data': ParticipantSerializer(participant).data
            }, status=status.HTTP_200_OK)

        except Participant.DoesNotExist:
            return Response({'error': 'Participant not found for this tournament.'}, status=status.HTTP_404_NOT_FOUND)


class UpdateFeaturedTournamentView(APIView):
    def patch(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({'error': 'Tournament not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Toggle the featured status
        tournament.featured = not tournament.featured  # If True -> False, if False -> True
        tournament.save()

        serializer = TournamentSerializer(tournament)
        return Response({
            'success': True,
            'message': 'Featured status updated successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)




class FeaturedTournamentListView(APIView):
    def get(self, request):
        today = timezone.now().date()
        tournaments = Tournament.objects.filter(featured=True, event_date__gt=today)

        if tournaments.exists():
            serializer = TournamentSerializer(tournaments, many=True)
            return Response({
                "success": True,
                "message": "Featured tournaments retrieved successfully.",
                "data": serializer.data
            })
        else:
            return Response({
                "success": False,
                "message": "No featured tournaments available.",
                "data": []
            })







class UserInactiveTournamentsAdminView(APIView):
    def get(self, request, user_id):
        try:
            # Step 1: Fetch the user
            user = User.objects.get(id=user_id)

            # Step 2: Fetch inactive tournaments created by the user
            inactive_tournaments = Tournament.objects.filter(
                created_by=user,
                is_active=False
            )

            # Step 3: Fetch participants for the filtered tournaments
            participants = Participant.objects.filter(
                tournament__in=inactive_tournaments
            ).select_related('tournament', 'user')

            # Step 4: Group participants by tournament
            tournament_participants_map = defaultdict(list)
            for participant in participants:
                tournament_participants_map[participant.tournament].append(participant)

            # Step 5: Prepare the final data structure
            result = []
            for tournament, participants_list in tournament_participants_map.items():
                result.append({
                    "tournament": TournamentSerializer(tournament).data,
                    "participants": ParticipantSerializernewhistory(participants_list, many=True).data,
                })

            return Response({
                "success": True,
                "message": "Inactive tournaments and their participants retrieved successfully.",
                "data": result,
                "current_date": now().date(),
                "current_time": now().strftime('%H:%M:%S'),
                "timezone": "Asia/Karachi",
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "User not found.",
                "data": []
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e),
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class UserInactiveTournamentsAdminView(APIView):
#     def get(self, request, user_id):
#         try:
#             user = User.objects.get(id=user_id)

#             # Step 1: Fetch inactive tournaments created by the user
#             inactive_tournaments = Tournament.objects.filter(
#                 created_by=user,
#                 is_active=False
#             )

#             # Step 2: Fetch participants for the filtered tournaments
#             participants = Participant.objects.filter(
#                 tournament__in=inactive_tournaments
#             ).select_related('tournament', 'user')

#             # Step 3: Serialize participants
#             serializer = ParticipantSerializernewhistory(participants, many=True)

#             return Response({
#                 "success": True,
#                 "message": "Inactive tournaments and their participants retrieved successfully.",
#                 "data": serializer.data,
#                 "current_date": now().date(),
#                 "current_time": now().strftime('%H:%M:%S'),
#                 "timezone": "Asia/Karachi",
#             }, status=status.HTTP_200_OK)

#         except User.DoesNotExist:
#             return Response({
#                 "success": False,
#                 "message": "User not found.",
#                 "data": []
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 "success": False,
#                 "message": str(e),
#                 "data": []
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
