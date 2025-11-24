from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Voter, TempVoter
import requests
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2
from django.forms.models import model_to_dict
from .models import AdminLog, LoginLog
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now

FASTAPI_URL = "http://127.0.0.1:8001"

## Save Voter Details in TempTable
@receiver(post_save, sender=Voter)
def save_voter_to_temp(sender, instance, created, **kwargs):
    if created:
        TempVoter.objects.create(
            batch_id=1,
            state_name=instance.state.name if instance.state else '',
            constituency_name=instance.constituency.name if instance.constituency else '',
            full_name=instance.name,
            dob=instance.dob,
            gender=instance.gender,
            phone=instance.phone,
            address=instance.address,
            is_valid=True
        )

## Save User Info
#@receiver(user_logged_in)
#def log_admin_login(sender, request, user, **kwargs):
#    # Only log AdminUser
#    if hasattr(user, 'adminuser'):  # Assuming you have a OneToOne to AdminUser
#        admin_user = user.LoginLog
#
#        # Get IP address
#        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#        if x_forwarded_for:
#            ip = x_forwarded_for.split(',')[0]
#        else:
#            ip = request.META.get('REMOTE_ADDR')
#
#        # Get device info from User-Agent
#        device_info = request.META.get('HTTP_USER_AGENT', '')
#
##        # Optionally get geolocation from IP (requires external service)
#        latitude = None
#        longitude = None
#        # Example: use geolocation API like ipstack or GeoIP2
#        # from django.contrib.gis.geoip2 import GeoIP2
#        # g = GeoIP2()
#        # try:
#        #     location = g.city(ip)
#        #     latitude = location['latitude']
#        #     longitude = location['longitude']
#        # except:
#        #     pass
#
#        # Save login record
#        LoginLog.objects.create(
#            admin=admin_user,
#            ip_address=ip,
#            device_info=device_info,
#            login_time=timezone.now()
#        )

##==============================
    #Log Report of User
##==============================
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    location = get_location(ip)
    latitude = location.get('latitude') if location else None
    longitude = location.get('longitude') if location else None

    device = request.META.get('HTTP_USER_AGENT', '')
    role = "Admin" if user.is_staff else "Voter"
    
    admin_log = None
    if user.is_staff:
        admin_log, _ = AdminLog.objects.get_or_create(admin=user)

    LoginLog.objects.create(
        admin = admin_log,
        user=user,
        role=role,
        ip_address=ip,
        device_info=device,
        latitude=latitude,
        longitude=longitude,
        action=request.path,  # store which page they accessed
        login_time=now()
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location(ip):
    # ignore localhost
    if ip.startswith("127.") or ip == "localhost":
        return None

    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        if response.status_code == 200:
            data = response.json()
            return {
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
            }
    except:
        pass

    return None
 
@receiver(post_save, sender=Voter)
def register_voter_face(sender, instance, created, **kwargs):
    if created and instance.photo_url:  # If new voter and photo uploaded
        try:
            with open(instance.photo_url, "rb") as f:
                files = {"file": f}
                resp = requests.post(f"{FASTAPI_URL}/register_face/", data={"voter_id": instance.id}, files=files)
                print(resp.json())
        except Exception as e:
            print("Face registration failed:", e)


@receiver(post_save, sender=Voter)
def log_voter_changes(sender, instance, created, **kwargs):
    user = User.objects.first()  # Replace with request.user in views
    old_data = getattr(instance, "_old_data", {})
    new_data = model_to_dict(instance)
    if not created:
        changes = []
        for field in new_data:
            old = old_data.get(field)
            new = new_data.get(field)
            if old != new:
                changes.append(f"{field}: {old} -> {new}")
        if changes:
            AdminLog.objects.create(
                admin=user,
                action="Voter Updated",
                details="; ".join(changes)
            )
