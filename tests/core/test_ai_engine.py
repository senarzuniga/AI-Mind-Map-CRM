import unittest
from unittest.mock import patch, MagicMock
from core.ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    @patch('core.ai_engine.ExternalService')
    def test_ai_engine_with_mocked_service(self, MockExternalService):
        # Arrange
        mock_service_instance = MockExternalService.return_value
        mock_service_instance.some_method.return_value = 'mocked result'
        ai_engine = AIEngine()

        # Act
        result = ai_engine.process_data()

        # Assert
        self.assertEqual(result, 'expected result based on mocked result')

if __name__ == '__main__':
    unittest.main()
