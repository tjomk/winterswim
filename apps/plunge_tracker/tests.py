from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json


class WeatherServiceTest(TestCase):
    """Test cases for the weather service integration."""
    
    def set_up_mock_weather_response(self):
        """Set up a mock response for Open-Meteo API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current_weather': {
                'temperature': 12.5,
                'windspeed': 4.2,
                'winddirection': 315,
                'time': '2024-01-15T12:00'
            }
        }
        return mock_response
        
    @patch('apps.plunge_tracker.services.weather_service.OpenMeteoService.get_current_weather')
    def test_weather_api_endpoint_success(self, mock_get_weather):
        """Test that the weather API endpoint returns correct data."""
        # Mock the weather service response
        mock_get_weather.return_value = {
            'temperature': 12.5,
            'windspeed': 4.2,
            'winddirection': 315,
            'time': '2024-01-15T12:00'
        }
        
        client = Client()
        response = client.get(reverse('plunge_tracker:get_weather_data'), {
            'latitude': 59.4370,
            'longitude': 24.7536
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['temperature'], 12.5)
        self.assertEqual(data['data']['windspeed'], 4.2)
        self.assertEqual(data['data']['winddirection'], 'NW')  # 315 degrees = NW
        
    def test_weather_api_endpoint_invalid_coordinates(self):
        """Test that invalid coordinates return an error."""
        client = Client()
        
        # Test with invalid latitude
        response = client.get(reverse('plunge_tracker:get_weather_data'), {
            'latitude': 200,  # Invalid latitude
            'longitude': 24.7536
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
    def test_weather_api_endpoint_missing_parameters(self):
        """Test that missing parameters return an error."""
        client = Client()
        
        # Test with missing latitude
        response = client.get(reverse('plunge_tracker:get_weather_data'), {
            'longitude': 24.7536
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class PlungeTrackerViewTest(TestCase):
    """Test cases for the plunge tracker views."""
    
    def test_plunge_list_view(self):
        """Test that the plunge list view renders correctly."""
        response = self.client.get(reverse('plunge_tracker:plunge_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plunge_tracker/plunge_list.html')
        self.assertContains(response, 'My Winter Swims')
