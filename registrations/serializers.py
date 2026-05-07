from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """Validates the Kwekwe Golf Day registration payload.

    Required: full_name, email, phone. Everything else is optional.
    """

    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40)

    company = serializers.CharField(max_length=120, required=False, allow_blank=True)
    handicap = serializers.CharField(max_length=20, required=False, allow_blank=True)
    team_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_2_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_3_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_4_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    tee_preference = serializers.CharField(max_length=80, required=False, allow_blank=True)
    dietary_requirements = serializers.CharField(max_length=500, required=False, allow_blank=True)
    special_requests = serializers.CharField(max_length=1000, required=False, allow_blank=True)
