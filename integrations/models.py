from django.db import models

class Integration(models.Model):
    INTEGRATION_TYPES = (
        ('generic', 'Generic'),
        ('telegram', 'Telegram'),
        # Add more types as needed
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='integrations'
    )
    type = models.CharField(max_length=50, choices=INTEGRATION_TYPES, default='generic')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    

    class Meta:
        verbose_name = "Integration"
        verbose_name_plural = "Integrations"
        ordering = ['-created_at']

class TelegramIntegration(Integration):
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.type = 'telegram'
        self.id = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Telegram Integration: {self.name} - {self.user.username}"

    class Meta:
        verbose_name = "Telegram Integration"
        verbose_name_plural = "Telegram Integrations"
        ordering = ['-created_at']