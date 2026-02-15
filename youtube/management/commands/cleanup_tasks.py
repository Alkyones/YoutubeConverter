from django.core.management.base import BaseCommand
from youtube.models import DownloadTask

class Command(BaseCommand):
    help = 'Clean up corrupted DownloadTask records with null IDs'

    def handle(self, *args, **options):
        try:
            # Delete all existing tasks (they have corrupted IDs)
            deleted_count, _ = DownloadTask.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} corrupted tasks'
                )
            )
            
            # Verify cleanup
            remaining_count = DownloadTask.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Remaining tasks: {remaining_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning tasks: {str(e)}')
            )