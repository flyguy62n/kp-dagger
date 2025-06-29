"""Test base parser functionality."""

from pybastion.parsers.base.parser import BaseParser


class TestParser(BaseParser):
    """Test implementation of BaseParser."""

    def parse(self, config_text: str) -> dict:
        """Test parse method."""
        return {"hostname": self._extract_hostname(config_text)}

    def can_parse(self, config_text: str) -> bool:
        """Test can_parse method."""
        return "test" in config_text.lower()


def test_base_parser_initialization():
    """Test BaseParser initialization."""
    parser = TestParser()
    assert parser.parsed_data == {}
    assert parser.raw_config == ""
    assert parser.errors == []


def test_extract_hostname():
    """Test hostname extraction."""
    parser = TestParser()
    config = "hostname test-router\ninterface GigabitEthernet0/0"
    hostname = parser._extract_hostname(config)
    assert hostname == "test-router"


def test_parse_lines():
    """Test line parsing."""
    parser = TestParser()
    config = "line 1\n  line 2  \n\nline 3\n"
    lines = parser._parse_lines(config)
    assert lines == ["line 1", "  line 2", "line 3"]


def test_error_handling():
    """Test error handling."""
    parser = TestParser()
    parser._add_error("Test error")
    assert "Test error" in parser.get_errors()

    parser.clear_errors()
    assert parser.get_errors() == []
