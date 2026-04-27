"""Pytest configuration for python_single tests."""

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: integration test that invokes external tools (lualatex, dvisvgm)",
    )
