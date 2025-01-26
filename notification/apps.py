import threading
import time
from datetime import datetime
from django.apps import AppConfig
from django.db import connections
from django.db.utils import OperationalError

thread_started = False  # Global flag to prevent multiple threads

class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification"

    def ready(self):
        global thread_started
        if not thread_started:
            thread_started = True
            print("Starting Notification Service...")
            threading.Thread(target=start_notification_service, daemon=True).start()


def start_notification_service():
    # Wait for Django to fully initialize
    time.sleep(5)
    print("Notification Service started.")

    while True:
        try:
            # Ensure the database connection is alive
            for conn in connections.all():
                conn.close_if_unusable_or_obsolete()

            # Import models here to avoid circular import issues
            from notification.models import Notification
            from Tournaments.models import Tournament, Participant

            now = datetime.now().date()
            print(f"[{datetime.now()}] Checking active tournaments for {now}...")

            active_tournaments = Tournament.objects.filter(
                is_active=True,
                event_date=now
            )

            if active_tournaments.exists():
                print(f"Found {active_tournaments.count()} active tournaments.")

            for tournament in active_tournaments:
                participants = Participant.objects.filter(
                    tournament=tournament,
                    is_disqualified=False
                )

                print(f"Tournament '{tournament.tournament_name}' has {participants.count()} participants.")

                for participant in participants:
                    notification, created = Notification.objects.get_or_create(
                        user=participant.user,
                        title=f"Reminder: '{tournament.tournament_name}' starts today!",
                        message=(
                            f"The tournament '{tournament.tournament_name}' is happening today at "
                            f"{tournament.event_start_time}. Get ready!"
                        )
                    )

                    if created:
                        print(f"Notification created for user {participant.user.username}.")
                    else:
                        print(f"Notification already exists for user {participant.user.username}.")

            print(f"[{datetime.now()}] Notification processing complete. Sleeping for 12 hours...")

            # Wait for 12 hours before running again
            time.sleep(12 * 60 * 60)

        except OperationalError:
            print(f"[{datetime.now()}] Database connection error. Retrying in 60 seconds...")
            time.sleep(60)
        except Exception as e:
            print(f"[{datetime.now()}] Unexpected error: {str(e)}. Retrying in 60 seconds...")
            time.sleep(60)
