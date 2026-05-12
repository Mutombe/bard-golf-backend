import logging

from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .serializers import RegistrationSerializer, NewsletterSerializer
from .sheets import append_registration, append_newsletter


log = logging.getLogger(__name__)


def _client_ip(request) -> str:
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


@api_view(['GET'])
def health(request):
    """Liveness probe."""
    return Response({'status': 'ok'})


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def register(request):
    """Accept a Kwekwe Golf Day registration and append it to the sheet."""
    serializer = RegistrationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'ok': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cell = append_registration(
            serializer.validated_data,
            source_ip=_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    except Exception as exc:
        log.exception('Failed to append registration to sheet')
        return Response(
            {'ok': False, 'error': 'Could not record registration. Please try again.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            'ok': True,
            'message': (
                'Thank you for your registration. A member of our team will be in '
                'touch shortly with confirmation and tee-time details.'
            ),
            'reference': cell,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def newsletter(request):
    """Accept a newsletter subscription and append it to the sheet."""
    serializer = NewsletterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'ok': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = serializer.validated_data
    try:
        cell = append_newsletter(
            email=data['email'],
            source=data.get('source', ''),
            source_ip=_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
    except Exception:
        log.exception('Failed to append newsletter subscriber to sheet')
        return Response(
            {'ok': False, 'error': 'Could not record your subscription. Please try again.'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            'ok': True,
            'message': 'You are on the list. The next season dispatch will arrive when the season opens.',
            'reference': cell,
        },
        status=status.HTTP_201_CREATED,
    )
