# urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('adminstartmatch/<int:tournament_id>/', adminstartmatch.as_view(), name='update_fixtures_start_time'),
    path('participant_ready/<int:participant_id>/', UpdateParticipantReadyStatus.as_view(), name='update-participant-ready'),
    path('api/decks/create/', DeckCreateView.as_view(), name='create-deck'),
    path('create-tournament/', TournamentCreateView.as_view(), name='create-tournament'),
    path('getalltournaments/', TournamentListView.as_view(), name='tournament-list'),
    path('allgames/', GameListView.as_view(), name='game-list'),  # Add this line
    path('tournaments/<int:tournament_id>/register/', RegisterForTournamentView.as_view(), name='register_for_tournament'),
    path('api/match_scores/tournament/<int:tournament_id>/', get_match_scores_by_tournament, name='get_match_scores_by_tournament'),
    path('featured-tournaments/', featured_tournament_list, name='featured_tournament_list'),
    path('create/featured-tournament/', create_featured_tournament, name='create_featured_tournament'),
    path('create/banner-image/', create_banner_image, name='create_banner_image'),
    # URL for retrieving a specific featured tournament by id
    path('featured-tournaments/<int:pk>/', featured_tournament_detail, name='featured_tournament_detail'),
    path('api/featured-tournaments/', FeaturedTournamentListView.as_view(), name='featured-tournaments'),
    path('tournaments_events/<int:game_id>/', TournamentByGameView.as_view(), name='tournaments_by_game'),
    path('api/participants/<int:user_id>/', UserParticipantsView.as_view(), name='user-participants'),
    # URL for listing all banner images
    path('delete_banner/<int:banner_id>/', delete_banner_image, name='delete-banner'),
    path('banner-images/', list_banner_images, name='banner_image_list'),
    path('pokemon_cards/', PokemonCardsView.as_view(), name='pokemon-cards'),
    path('magicthegatherin_cards/', fetch_cards, name='fetch_cards'),
    path('add_decks/<int:deck_id>/', AddMultipleCardsView.as_view(), name='add-multiple-cards'),
    path('getuserdeck/<int:user_id>/game/<int:game_id>/', UserGameDecksView.as_view(), name='user_game_decks'),
    path('getuserdeckdata/<int:user_id>/game/<int:game_id>/', UserGameDecksViewnew.as_view(), name='user_game_decks'),
    # URL for retrieving a specific banner image by id
    path('banner-images/<int:pk>/', banner_image_detail, name='banner_image_detail'),
    path('tournaments/draft/create/<int:user_id>/', TournamentViewSet.as_view({'post': 'save_draft'}), name='save_draft'),
    path('tournaments/active/', TournamentViewSet.as_view({'get': 'active'}), name='active_tournaments'),
    path('tournaments/active/new/', TournamentViewSet.as_view({'get': 'newactive'}), name='active_tournaments'),
    path('tournaments/drafts/<int:user_id>/', TournamentViewSet.as_view({'get': 'drafts'}), name='drafts_by_user'),
    path('tournaments/<int:pk>/', TournamentViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='tournament_detail'),
    path('tournaments/<int:pk>/convert_to_actual/', TournamentViewSet.as_view({'post': 'convert_to_actual'}), name='convert_draft_to_actual'),
    path('tournaments/<int:pk>/update_draft/', TournamentViewSet.as_view({'put': 'update_draft'}), name='update_draft'),
    path('tournaments/<int:tournament_id>/disqualify_user/<int:user_id>/', TournamentViewSet.as_view({'post': 'disqualify_user'})),
    path('participants/arrive-at-venue/', ParticipantViewSet.as_view({'patch': 'arrive_at_venue'}), name='arrive-at-venue'),
    path('tournaments/<int:pk>/eligible-participants/', TournamentViewSet.as_view({'get': 'eligible_participants'}), name='eligible-participants'),
    path('tournaments/<int:pk>/Tournament_participants/', TournamentViewSet.as_view({'get': 'Tournament_participants'}), name='Tournament_participants'),
    path('gettournaments/', TournamentViewSet.as_view({'get': 'all_tournaments'}), name='all-tournaments'),  # To get all tournaments
    path('create_feature/<int:tournament_id>/', UpdateFeaturedTournamentView.as_view(), name='update-featured'),
    path('myfixture/<int:tournament_id>/<int:user_id>/', UserTournamentFixturesView.as_view(), name='user-tournament-fixtures'),
    path('tournaments/<int:pk>/create_round_1_fixtures/', FixtureViewSet.as_view({'post': 'create_round_1_fixtures'}), name='create-round-1-fixtures'),
    path('fixtures/<int:pk>/advance_to_next_round/', FixtureViewSet.as_view({'post': 'advance_to_next_round'}), name='advance_to_next_round'),
    path('user/register/<int:user_id>/', register_for_tournament, name='register-for-tournament'),
    path('adminfixturelist/<int:tournament_id>/', admingetallTournamentFixturesView.as_view(), name='tournament-fixtures'),
    path('set_nominated_winner/<int:fixture_id>/',set_nominated_winner, name='set_nominated_winner'),
    path('set_verified_winner/<int:fixture_id>/', set_verified_winner, name='set_verified_winner'),
    path('set_verified_winnerall/', set_verified_winner_all, name='set_verified_winner'),
    path('fixtures/<int:pk>/create_fixtures/', FixtureViewSet.as_view({'post': 'manage_fixtures'}), name='manage-fixtures'),
    path('getrecent/<int:user_id>/', events_today, name='events_today'),
    path('admintoday/<int:user_id>/', TodayEventParticipantsView.as_view(), name='today_event_participants'),
    path('eliminate-participant/<int:fixture_id>/', eliminate_participant, name='eliminate_participant'),
    path('adminfixturelist/<int:tournament_id>/', admingetallTournamentFixturesView.as_view(), name='tournament-fixtures'),
    path('getallstaff/', StaffListView.as_view(), name='today_event_participants'),


    # # history
    # path('users_tournament_history/<int:user_id>/', UserTournamentHistoryAPIView, name='tournament-history'),
    path('users_tournament_history/<int:user_id>/', UserInactiveTournamentsView.as_view(), name='tournament-history'),
    path('users_admin_tournament_history/<int:user_id>/', UserInactiveTournamentsAdminView.as_view(), name='tournament-history'),
    # path('users_tournament_history/<int:user_id>/', UserInactiveTournamentsView.as_view(), name='tournament-history'),
    path('match_scores/<int:tournament_id>/', TournamentMatchScoresView.as_view(), name='tournament-match-scores'),
    path('deck/<str:deck_name>/', DeckByNameView.as_view(), name='deck-by-name'),
    path('top_players/', TopPlayersView.as_view(), name='top-players'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
