
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from magicapi_tools.utils.resource_manager import MagicAPIResourceManager

class TestResourceManagerAuth(unittest.TestCase):
    def test_login_extracts_token(self):
        # Mock response for login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 1}
        mock_response.headers = {"magic-token": "rm-token-456"}
        
        with patch("requests.Session") as MockSession:
            mock_session = MockSession.return_value
            mock_session.post.return_value = mock_response
            mock_session.headers = {}
            
            # Initialize manager (will call login)
            manager = MagicAPIResourceManager(
                base_url="http://test",
                username="user",
                password="pass"
            )
            
            # Verify login call
            # Note: The first call to post should be login
            # mock_session.post.assert_any_call(
            #     "http://test/login",
            #     data={'username': 'user', 'password': 'pass'}
            # )
            
            # Verify token extracted and put into session headers
            if "magic-token" in mock_session.headers:
                print("Token found in session headers!")
            else:
                print("Token NOT found in session headers.")
                
            self.assertEqual(mock_session.headers.get("magic-token"), "rm-token-456")
            
            # Test copy_group to ensure it doesn't override token
            mock_response_copy = MagicMock()
            mock_response_copy.status_code = 200
            mock_response_copy.json.return_value = {"code": 1, "data": "new-group-id"}
            mock_session.post.return_value = mock_response_copy
            
            manager.copy_group("src-id", "target-id")
            
            # Get the arguments of the last call
            args, kwargs = mock_session.post.call_args
            self.assertEqual(args[0], "http://test/resource/folder/copy")
            headers = kwargs.get('headers', {})
            
            # Ensure 'magic-token' is NOT in the explicitly passed headers
            # If it were there, it would override the session header (possibly with 'unauthorization' if I hadn't fixed it)
            self.assertNotIn("magic-token", headers)
            print("Verified: magic-token is not overridden in copy_group headers")

if __name__ == "__main__":
    unittest.main()
