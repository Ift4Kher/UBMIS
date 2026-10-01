from django.db import models

# Create your models here.
class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Slider Image {self.id}"

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
    )
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    admin_reply = models.TextField(blank=True, null=True) # Deprecated, moving to ComplaintMessage but keeping for history
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint by {self.user.username}: {self.subject}"

class ComplaintMessage(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username}"

class SiteSetting(models.Model):
    auth_image = models.ImageField(upload_to='site_settings/', help_text="Image displayed on the left side of Login/Register pages")
    site_logo = models.ImageField(upload_to='site_settings/', blank=True, null=True, help_text="Logo displayed on top of the auth image (optional)")
    
    booking_start_time = models.TimeField(default='00:00:00', help_text="Global time when booking opens for all buses")
    booking_end_time = models.TimeField(default='23:59:59', help_text="Global time when booking closes for all buses")
    
    shuttle_booking_start_time = models.TimeField(default='00:00:00', help_text="Time when booking opens for SHUTTLE buses")
    shuttle_booking_end_time = models.TimeField(default='23:59:59', help_text="Time when booking closes for SHUTTLE buses")
    
    booking_activation_datetime = models.TimeField(null=True, blank=True, help_text="Specific time when REGULAR booking becomes active (Daily)")
    shuttle_booking_activation_datetime = models.TimeField(null=True, blank=True, help_text="Specific time when SHUTTLE booking becomes active (Daily)")
    current_operating_date = models.DateField(default=__import__('django.utils.timezone').utils.timezone.now, help_text="The date for which schedules are currently displayed on the home page")
    
    homepage_video = models.FileField(upload_to='site_settings/videos/', blank=True, null=True, help_text="Video displayed on the home page under Routes section")

    def __str__(self):
        return "Site Configuration"

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
