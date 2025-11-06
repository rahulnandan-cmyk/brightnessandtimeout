# hello_world_test.py
"""A simple Mobly test to demonstrate basic functionality."""

from mobly import base_test

class HelloWorldTest(base_test.BaseTestClass):
    """A minimal Mobly test class."""

    def setup_class(self):
        """Sets up the test class before any test cases are run."""
        self.log.info("Starting setup for the test class.")

    def teardown_class(self):
        """Cleans up the test class after all test cases have finished."""
        self.log.info("Tearing down the test class.")

    def test_hello_world(self):
        """A simple test case that prints a message to the log."""
        self.log.info("Hello, World! This is a simple Mobly test.")
        # Simple assertion
        self.assert_equal(1, 1, "This assertion should pass.")
        self.log.info("Test passed successfully!")

    def test_basic_math(self):
        """Another simple test case."""
        self.log.info("Running basic math test.")
        result = 2 + 2
        self.assert_equal(result, 4, "2 + 2 should equal 4")
        self.log.info(f"Math test passed: 2 + 2 = {result}")

if __name__ == "__main__":
    # This allows running the test directly
    from mobly import test_runner
    import sys
    
    # Run the test using Mobly's test runner
    test_runner.main([sys.argv[0]])