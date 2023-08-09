"""
Formatting utilities tests.
"""
from template.utils.formatting import to_camel


class TestFormatting:
    """
    Formatting utilities tests cases.
    """

    def test_to_camel_snake_case(self):
        """
        GIVEN a string in snake case
        WHEN the string is translated to camel case
        THEN assert the string is translated correctly
        """
        foo = "foo_bar"

        assert to_camel(foo) == "fooBar"

    def test_to_camel_with_hyphen(self):
        """
        GIVEN a string in kebab case
        WHEN the string is translated to camel case
        THEN assert the string is translated correctly
        """
        foo = "foo-bar"

        assert to_camel(foo) == "fooBar"

    def test_to_camel_with_space(self):
        """
        GIVEN a string in space case
        WHEN the string is translated to camel case
        THEN assert the string is translated correctly
        """
        foo = "foo bar"

        assert to_camel(foo) == "fooBar"

    def test_to_camel_with_mixed_case(self):
        """
        GIVEN a string in mixed case
        WHEN the string is translated to camel case
        THEN assert the string is translated correctly
        """
        foo = "fOoBaR"

        assert to_camel(foo) == "foobar"

    def test_to_camel_with_multiple_separators(self):
        """
        GIVEN a string with multiple separators
        WHEN the string is translated to camel case
        THEN assert the string is translated correctly
        """
        foo = "foo_bar-baz"

        assert to_camel(foo) == "fooBarBaz"
