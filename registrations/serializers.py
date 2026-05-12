from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    """Validates the Kwekwe Golf Day registration payload.

    Required: full_name, email, phone. Everything else is optional so
    different forms (homepage card, dedicated register page) can submit
    different subsets without breaking validation.
    """

    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40)

    company = serializers.CharField(max_length=120, required=False, allow_blank=True)
    handicap = serializers.CharField(max_length=20, required=False, allow_blank=True)
    home_club = serializers.CharField(max_length=120, required=False, allow_blank=True)
    caddy = serializers.CharField(max_length=40, required=False, allow_blank=True)
    heard_about = serializers.CharField(max_length=120, required=False, allow_blank=True)
    prize_giving = serializers.CharField(max_length=40, required=False, allow_blank=True)

    team_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_2_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_3_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    player_4_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    tee_preference = serializers.CharField(max_length=80, required=False, allow_blank=True)
    dietary_requirements = serializers.CharField(max_length=500, required=False, allow_blank=True)
    special_requests = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    event = serializers.CharField(max_length=80, required=False, allow_blank=True)


class NewsletterSerializer(serializers.Serializer):
    """Validates the newsletter subscription payload."""

    email = serializers.EmailField()
    source = serializers.CharField(max_length=120, required=False, allow_blank=True)
