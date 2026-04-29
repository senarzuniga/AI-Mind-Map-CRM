import unittest
from unittest.mock import patch, MagicMock
from core.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    @patch('core.orchestrator.ExternalAPI')
    def test_orchestrator_with_mocked_api(self, MockExternalAPI):
        # Arrange
        mock_api_instance = MockExternalAPI.return_value
        mock_api_instance.fetch_data.return_value = {'key': 'mocked value'}
        orchestrator = Orchestrator()

        # Act
        data = orchestrator.get_data()

        # Assert
        self.assertEqual(data, {'key': 'expected value based on mocked value'})

if __name__ == '__main__':
    unittest.main()
