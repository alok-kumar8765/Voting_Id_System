from django import forms
from .models import Voter
import random

def generate_unique_code(length=8):
    """
    Generate a globally unique numeric code of given length.
    Checks existing codes in the DB to avoid collisions.
    """
    while True:
        code = f"{random.randint(0, 10**length - 1):0{length}d}"  # zero-padded
        if not Voter.objects.filter(unique_code=code).exists():
            return code

class VoterForm(forms.ModelForm):
    aadhaar = forms.CharField(
        max_length=12,
        min_length=12,
        required=True,
        help_text="Enter 12-digit Aadhaar number",
        widget=forms.TextInput(attrs={'placeholder': '12-digit Aadhaar'})
    )

    class Meta:
        model = Voter
        fields = ['name', 'phone', 'date_of_birth', 'aadhaar']

    def clean_aadhaar(self):
        aadhaar = self.cleaned_data['aadhaar']
        if not aadhaar.isdigit():
            raise forms.ValidationError("Aadhaar must contain only digits.")
        return aadhaar

    def save(self, commit=True):
        # Create instance but don’t save yet
        instance = super().save(commit=False)
        
        # Encrypt and set Aadhaar
        instance.set_aadhaar(self.cleaned_data['aadhaar'])
        
        # Generate unique code automatically
        instance.unique_code = generate_unique_code(length=8)
        
        if commit:
            instance.save()
        return instance
