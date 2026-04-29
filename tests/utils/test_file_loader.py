import unittest
from unittest.mock import patch, mock_open
from utils.file_loader import FileLoader

class TestFileLoader(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='mocked file content')
    def test_file_loader_with_mocked_file(self, mock_file):
        # Arrange
        file_loader = FileLoader()

        # Act
        content = file_loader.load_file('dummy_path')

        # Assert
        self.assertEqual(content, 'mocked file content')

if __name__ == '__main__':
    unittest.main()
