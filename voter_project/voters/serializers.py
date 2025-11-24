from rest_framework import serializers
from .models import Voter
import random
from datetime import date

def generate_unique_code(length=8):
    """
    Generate a globally unique numeric code of given length.
    Checks existing codes in the DB to avoid collisions.
    """
    while True:
        code = f"{random.randint(0, 10**length - 1):0{length}d}"  # zero-padded
        if not Voter.objects.filter(unique_code=code).exists():
            return code

class VoterSerializer(serializers.ModelSerializer):
    aadhaar = serializers.CharField(
        write_only=True,  # Never expose Aadhaar in API
        min_length=12,
        max_length=12
    )
    age = serializers.SerializerMethodField()
    state = serializers.StringRelatedField()
    constituency = serializers.StringRelatedField()
    booth = serializers.StringRelatedField()
    
    class Meta: 
        model = Voter 
        fields = '__all__'
    
    def validate_aadhaar(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Aadhaar must contain only digits.")
        return value

    def create(self, validated_data):
        aadhaar = validated_data.pop('aadhaar')
        voter = Voter(**validated_data)
        voter.set_aadhaar(aadhaar)  # Encrypt before saving
        voter.unique_code = generate_unique_code(length=8)
        voter.save()
        return voter
    
    def update(self, instance, validated_data):
        if 'aadhaar' in validated_data:
            aadhaar = validated_data.pop('aadhaar')
            instance.set_aadhaar(aadhaar)
        return super().update(instance, validated_data)
    
    def get_age(self, obj):
        return obj.age_on_year(date.today().year)
