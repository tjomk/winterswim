from infrastructure.weather.open_meteo_service import OpenMeteoService
from typing import Optional, Dict, Any


class WeatherService:
    """
    Service layer for weather-related operations.
    
    This service acts as a facade to external weather APIs and provides
    a consistent interface for the application.
    """
    
    def __init__(self):
        self.open_meteo_service = OpenMeteoService()
        
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get current weather data for given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data or None if request fails
        """
        return self.open_meteo_service.get_current_weather(latitude, longitude)
        
    def convert_wind_direction_to_compass(self, degrees: float) -> str:
        """
        Convert wind direction in degrees to compass direction.
        
        Args:
            degrees: Wind direction in degrees (0-360)
            
        Returns:
            Compass direction abbreviation (N, NE, E, SE, S, SW, W, NW)
        """
        if degrees is None:
            return ""
            
        directions = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
        ]
        
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]