# run_extraction.py
import sys
from pathlib import Path

# Add project root to the Python path to allow for absolute imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.pdf_extractor import extract_and_clean_pdf

# Mock Streamlit functions as they are not available in a non-Streamlit context
# and are only used for UI feedback (progress bars, spinners, etc.)
class MockStreamlit:
    def progress(self, *args, **kwargs):
        class MockProgress:
            def progress(self, *args, **kwargs):
                pass
        return MockProgress()

    def spinner(self, *args, **kwargs):
        class MockSpinner:
            def __enter__(self):
                pass
            def __exit__(self, *args, **kwargs):
                pass
        return MockSpinner()
    
    def write(self, *args, **kwargs):
        print(*args, **kwargs)

    def error(self, *args, **kwargs):
        print("ERROR:", *args, **kwargs)
        
    def success(self, *args, **kwargs):
        print("SUCCESS:", *args, **kwargs)

    def warning(self, *args, **kwargs):
        print("WARNING:", *args, **kwargs)

    def info(self, *args, **kwargs):
        print("INFO:", *args, **kwargs)


# Replace streamlit module with our mock
sys.modules['streamlit'] = MockStreamlit()


if __name__ == "__main__":
    print("Starting PDF extraction process...")
    # The extract_and_clean_pdf function uses the mocked Streamlit,
    # so its UI calls will be replaced by print statements.
    extract_and_clean_pdf()
    print("PDF extraction process finished.")
