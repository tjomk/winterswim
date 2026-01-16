from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .services.weather_service import WeatherService
import logging

logger = logging.getLogger(__name__)

def plunge_list(request):
    return render(request, 'plunge_tracker/plunge_list.html', {})

@require_GET
@csrf_exempt
def get_weather_data(request):
    """
    API endpoint to fetch weather data for given coordinates.
    
    Expects GET parameters:
    - latitude: Latitude coordinate
    - longitude: Longitude coordinate
    
    Returns JSON response with weather data or error message.
    """
    try:
        latitude = float(request.GET.get('latitude'))
        longitude = float(request.GET.get('longitude'))
        
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return JsonResponse({
                'success': False,
                'error': 'Invalid coordinates'
            }, status=400)
            
        weather_service = WeatherService()
        weather_data = weather_service.get_current_weather(latitude, longitude)
        
        if weather_data:
            # Convert wind direction to compass format
            compass_direction = weather_service.convert_wind_direction_to_compass(
                weather_data.get('winddirection')
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'temperature': weather_data.get('temperature'),
                    'windspeed': weather_data.get('windspeed'),
                    'winddirection': compass_direction,
                    'time': weather_data.get('time')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Unable to fetch weather data'
            }, status=500)
            
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid coordinates in weather request: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid coordinates format'
        }, status=400)
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)