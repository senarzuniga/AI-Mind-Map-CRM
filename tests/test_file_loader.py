import io
import unittest
from utils.file_loader import load_file


class TestFileLoader(unittest.TestCase):
    def test_load_text_file(self):
        content = "Line 1\nLine 2\nLine 3"
        uploaded_file = io.BytesIO(content.encode('utf-8'))
        uploaded_file.name = "test.txt"

        result = load_file(uploaded_file)
        self.assertEqual(result, content)

    def test_load_text_file_with_unicode(self):
        content = "Línea 1\nLínea 2\nLínea 3"
        uploaded_file = io.BytesIO(content.encode('utf-8'))
        uploaded_file.name = "test.txt"

        result = load_file(uploaded_file)
        self.assertEqual(result, content)

    def test_load_text_file_with_large_content(self):
        content = "Line " * 10000
        uploaded_file = io.BytesIO(content.encode('utf-8'))
        uploaded_file.name = "test.txt"

        result = load_file(uploaded_file)
        self.assertEqual(result, content)


if __name__ == '__main__':
    unittest.main()
