import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OpenMeteoService:
    """
    Service for fetching weather data from Open-Meteo API.
    
    Documentation: https://open-meteo.com
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        self.timeout = 10  # seconds
        
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data or None if request fails
        """
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current_weather': 'true',
                'temperature_unit': 'celsius',
                'windspeed_unit': 'ms',
                'timezone': 'auto'
            }
            
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'current_weather' in data:
                current_weather = data['current_weather']
                return {
                    'temperature': current_weather.get('temperature'),
                    'windspeed': current_weather.get('windspeed'),
                    'winddirection': current_weather.get('winddirection'),
                    'time': current_weather.get('time')
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Open-Meteo API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing Open-Meteo response: {e}")
            return None