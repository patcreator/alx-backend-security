from django.db import models

class RequestLog(models.Model):
    # This is like creating a form to store visitor information
    ip_address = models.GenericIPAddressField()  # Stores the IP address
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto-sets the time
    path = models.CharField(max_length=255)  # Stores which page they visited
    
    def __str__(self):
        # This is just for display purposes
        return f"{self.ip_address} - {self.timestamp}"