import sys
from pathlib import Path

# Add backend directory to sys.path so tests can import modules
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark the test as an asyncio test."
    )
