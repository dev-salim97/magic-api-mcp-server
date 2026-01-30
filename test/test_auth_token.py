
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import inspect

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from magicapi_tools.utils.http_client import MagicAPIHTTPClient
from magicapi_mcp.settings import MagicAPISettings

print(f"MagicAPISettings file: {inspect.getfile(MagicAPISettings)}")
print(f"MagicAPISettings from_env: {MagicAPISettings.from_env}")

class TestAuthToken(unittest.TestCase):
    def test_login_extracts_token(self):
        # Create settings directly to avoid from_env issues if any, 
        # but let's try to fix the test to use what works.
        # It seems safer to mock the settings object entirely since we only need it to hold values.
        
        settings = MagicMock(spec=MagicAPISettings)
        settings.base_url = "http://test"
        settings.username = "user"
        settings.password = "pass"
        settings.auth_enabled = True
        settings.timeout_seconds = 30
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 1}
        mock_response.headers = {"magic-token": "test-token-123"}
        
        # Mock requests.Session
        with patch("requests.Session") as MockSession:
            mock_session_instance = MockSession.return_value
            mock_session_instance.post.return_value = mock_response
            # Initialize headers as a real dict so we can check updates
            mock_session_instance.headers = {}
            
            # Initialize client (which calls _login)
            client = MagicAPIHTTPClient(settings=settings)
            
            # Verify login was called
            mock_session_instance.post.assert_called()
            
            # Verify token is in headers
            if "magic-token" in mock_session_instance.headers:
                print("Token found in headers!")
            else:
                print("Token NOT found in headers.")
            
            self.assertEqual(mock_session_instance.headers.get("magic-token"), "test-token-123")

if __name__ == "__main__":
    unittest.main()
