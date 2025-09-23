from django.db import models

class Conversation(models.Model):
    user_id = models.CharField(max_length=255)   # session ID or UUID
    step = models.CharField(max_length=20, default="intro")

    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.name or 'Anonymous'} (step: {self.step})"
