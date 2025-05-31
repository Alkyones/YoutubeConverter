from django.db import models

# Create your models here.
class Integration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='integrations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name - f" {self.user.username}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"
        ordering = ['-created_at']  # Order by creation date, newest first


class TelegramIntegration(Integration):
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Telegram Integration: {self.name} - {self.user.username}"

    class Meta:
        verbose_name = "Telegram Integration"
        verbose_name_plural = "Telegram Integrations"
        ordering = ['-created_at']