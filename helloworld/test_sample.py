import logging
from mobly import base_test
from mobly import test_runner

# Create a logger instance for this module
LOG = logging.getLogger(__name__)

class HelloWorldTest(base_test.BaseTestClass):
    """Simple Mobly test class."""

    def setup_class(self):
        # Runs once before all test cases
        LOG.info("Setting up HelloWorld test class.")

    def test_hello_world(self):
        # A simple test case
        LOG.info("Hello, Mobly test framework!")

    def teardown_class(self):
        # Runs once after all test cases
        LOG.info("Tearing down HelloWorld test class.")

if __name__ == "__main__":
    test_runner.main()
