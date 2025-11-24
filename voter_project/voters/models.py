from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from cryptography.fernet import Fernet  # Example AES encryption
from datetime import date

##=================================================
    # Functional Code For Unique Code Generate
##=================================================
def generate_unique_code():
    while True:
        code = f"{random.randint(0, 99999999):08d}"  # 8 digits with leading zeros
        if not Voter.objects.filter(unique_code=code).exists():
            return code
class State(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    epic_prefix = models.CharField(max_length=5, unique=True)
    
    def __str__(self):
        return f"{self.name}"
    
class Constituency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}"
    
class Booth(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    max_voter_capacity = models.IntegerField(default=1200)
    wheelchair_access = models.BooleanField(default=False)
    ramp_available = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}"
    
class Voter(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, null=True, blank=True)

    epic_number = models.CharField(max_length=20, unique=True,blank=True)
    unique_code = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    
    aadhaar_validator = RegexValidator(regex=r'^\d{12}$', message="Aadhaar number must be 12 digits.")
    aadhaar_encrypted = models.BinaryField(null=True, blank=True, validators=[aadhaar_validator])  # AES encrypted
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10,choices=[('Male', _('Male')),('Female', _('Female')),('Other', _('Other')),],default="Male")

    relative_name = models.CharField(max_length=20, default='None')
    relation_type = models.CharField(max_length=255, blank=True, choices=[('Father', _('Father')),('Mother', _('Mother')),('Son', _('Son')),('Husband', _('Husband')),('Other', _('Other'))],default='Father')

    address = models.TextField()
    house_number = models.CharField(max_length=255, blank=False,  default=0)
    phone_validator = RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits.")
    phone = models.CharField(max_length=10, validators=[phone_validator])

    photo_url = models.CharField(max_length=255, blank=True)
    signature_url = models.CharField(max_length=255, blank=True)

    #status = models.CharField(max_length=20, choices=[('active','Active'),('inactive','Inactive'),('migrated','Migrated'),('deleted','Deleted'),('dead','Dead')],default='active')
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', _('Active')),
            ('inactive', _('Inactive')),
            ('migrated', _('Migrated')),
            ('deleted', _('Deleted')),
            ('dead', _('Dead'))
        ],
        default='active'
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.epic_number})"
    
    ## Generate EPIC Number
    def generate_epic_number(self):
        # 10 digit random number
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        epic_prefix = self.state.code.upper()

        return f"{epic_prefix}{random_digits}"

    def save(self, *args, **kwargs):
        # Generate EPIC only once when new voter is created
        if not self.epic_number:
            epic = self.generate_epic_number()

            # ensure uniqueness
            while Voter.objects.filter(epic_number=epic).exists():
                epic = self.generate_epic_number()

            self.epic_number = epic

        super().save(*args, **kwargs)
    
    ## Check Voter's Age
    def age_on_year(self, year=None):
        """
        Returns age on a given year.
        If year is None, use current year.
        """
        if year is None:
            year = date.today().year

        # Compute birthday in the target year
        birth_month_day = self.date_of_birth.strftime('%m-%d')
        target_date = date(year, self.date_of_birth.month, self.date_of_birth.day)
        age = year - self.date_of_birth.year

        # Adjust if birthday hasn't happened yet in the target year
        if target_date > date(year, date.today().month, date.today().day):
            age -= 1
        return age

    age_on_year.short_description = "Age"
    
    ## If Voter is above 100 year Soft Delete
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    def soft_delete_if_over_100(self, admin_id=None):
        """
        Soft delete voter if age > 100 and record in DeathRecord and logs.
        """
        if self.age() > 100 and self.status != 'deleted':
            self.status = 'deleted'
            self.save()

            # Record in DeathRecord
            from .models import DeathRecord
            DeathRecord.objects.create(
                voter=self,
                death_certificate_number='AGE>100',
                certificate_url='',
                verified_by_admin=admin_id
            )

            # Log action (VoterLogs table)
            from .models import VoterLog
            VoterLog.objects.create(
                voter=self,
                action='deleted',
                admin_id=admin_id,
                comments='Age > 100 years'
            )
    ## Check For Below 18 Voter
    def clean(self):
        if self.age() < 18:
            raise ValidationError("Voter must be at least 18 years old.")

    def save(self, *args, **kwargs):
        self.clean()  # validate age before saving
        super().save(*args, **kwargs)
    
    ## Validate Adhaar Number must be 12 Digit Only
    def clean(self):
        # Validate aadhaar length before encrypting
        if self.aadhaar_encrypted:
            if len(self.aadhaar_encrypted) != 12 or not self.aadhaar_encrypted.isdigit():
                from django.core.exceptions import ValidationError
                raise ValidationError("Aadhaar must be 12 digits numeric only.")
                
    # Example AES key (in real use, store securely in environment)
    AES_KEY = Fernet.generate_key()

    def clean(self):
        """
        Validate aadhaar input before saving.
        """
        if hasattr(self, '_aadhaar_plain'):
            aadhaar_str = self._aadhaar_plain
            if not aadhaar_str.isdigit() or len(aadhaar_str) != 12:
                raise ValidationError("Aadhaar must be 12 digits numeric only.")

    def set_aadhaar(self, aadhaar_str):
        """
        Encrypt and set aadhaar number.
        """
        self._aadhaar_plain = aadhaar_str  # Store plain temporarily for validation
        self.clean()  # Validate before encrypting

        f = Fernet(self.AES_KEY)
        self.aadhaar_encrypted = f.encrypt(aadhaar_str.encode())

    def get_aadhaar(self):
        """
        Decrypt and return aadhaar number.
        """
        if not self.aadhaar_encrypted:
            return None
        f = Fernet(self.AES_KEY)
        return f.decrypt(self.aadhaar_encrypted).decode()

                
class AdminLog(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.admin}"

#=======================================================
    #For Extended Version
#=======================================================
class Address(models.Model):
    id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(
        Voter, 
        on_delete=models.CASCADE, 
        related_name='addresses'  # <- avoids clash with Voter.address field
    )    
    type = models.CharField(
        max_length=20,
        choices=[
            ('Permanent', _('Permanent')),
            ('Current', _('Current')),
            ('Previous', _('Previous')),
        ],
        default='Permanent'
    )
    full_address = models.TextField()
    house_number = models.CharField(max_length=6)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}"

class BiometricData(models.Model):
    biometric_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter,on_delete=models.CASCADE,related_name='biometric_data')
    fingerprint_data = models.BinaryField(blank=True, null=True)
    iris_scan_data = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"BiometricData for {self.voter.name}"

# FamilyRelations table
class FamilyRelation(models.Model):
    RELATION_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Husband', 'Husband'),
        ('Wife', 'Wife'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Guardian', 'Guardian'),
    ]

    relation_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='family_relations')
    relative_name = models.CharField(max_length=255)
    relation_type = models.CharField(max_length=20, choices=RELATION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.relative_name} ({self.relation_type})"


# DeathRecords table
class DeathRecord(models.Model):
    death_id = models.AutoField(primary_key=True)
    voter = models.OneToOneField(Voter, on_delete=models.CASCADE, related_name='death_record')
    death_certificate_number = models.CharField(max_length=255)
    certificate_url = models.CharField(max_length=255)
    verified_by_admin = models.IntegerField(blank=True, null=True)
    verified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"DeathRecord of {self.voter.name}"


# Notifications table
class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email')
    ]

    notification_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.voter.name}"


# UpdateLogs table
class UpdateLog(models.Model):
    update_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='update_logs')
    field_name = models.CharField(max_length=255)
    old_value = models.TextField()
    new_value = models.TextField()
    updated_by_admin = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"UpdateLog: {self.field_name} for {self.voter.name}"


# DuplicateCheckLog table
class DuplicateCheckLog(models.Model):
    check_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='duplicate_checks')
    duplicate_found = models.BooleanField(default=False)
    rule_matched = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)
    check_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"DuplicateCheck for {self.voter.name}"


# Localization table
class Localization(models.Model):
    id = models.AutoField(primary_key=True)
    key_name = models.CharField(max_length=255, unique=True)
    english_text = models.TextField()
    hindi_text = models.TextField(blank=True, null=True)
    regional_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.key_name


# MigrationHistory table
class MigrationHistory(models.Model):
    migration_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='migration_history')
    from_constituency = models.ForeignKey(Constituency, null=True, blank=True, on_delete=models.CASCADE, related_name='from_constituency')
    to_constituency = models.ForeignKey(Constituency, null=True, blank=True,on_delete=models.CASCADE, related_name='to_constituency')
    migrated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Migration of {self.voter.name}"


# BlacklistedVoters table
class BlacklistedVoter(models.Model):
    id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='blacklist_records')
    reason = models.TextField()
    suspended_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.voter.name} Blacklisted"



#class LoginLog(models.Model):
#    id = models.AutoField(primary_key=True)
#    admin = models.ForeignKey(AdminLog, on_delete=models.CASCADE, related_name='login_logs')
#    ip_address = models.CharField(max_length=45, blank=True, null=True)
#    device_info = models.TextField(blank=True, null=True)
#    latitude = models.FloatField(blank=True, null=True)
#    longitude = models.FloatField(blank=True, null=True)
#    login_time = models.DateTimeField(default=timezone.now)

#    def __str__(self):
#        return f"Login by {self.admin.username} at {self.login_time}"

from django.contrib.auth import get_user_model

User = get_user_model()  # Use the default Django user model

class LoginLog(models.Model):
    id = models.AutoField(primary_key=True)
    
    # Generic user reference
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Authenticated users
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, null=True, blank=True) # Track anonymous downloads
    admin = models.ForeignKey(AdminLog, on_delete=models.CASCADE, related_name='admin_logs',null=True, blank=True)
    
    # Optional role/description
    role = models.CharField(max_length=50, blank=True, null=True)  # e.g., SuperAdmin, Admin, Voter
    
    # Device/IP/location info
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    device_info = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Action or page visited (optional)
    action = models.CharField(max_length=255, blank=True, null=True)
    
    login_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Login by {self.user.username} ({self.role}) at {self.login_time}"


# TempVoters table
class TempVoter(models.Model):
    batch_id = models.IntegerField()
    state_name = models.CharField(max_length=100)
    constituency_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    relation_type = models.CharField(max_length=20, blank=True, null=True)
    relation_name = models.CharField(max_length=255, blank=True, null=True)

    is_valid = models.BooleanField(default=False)
    validation_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name
