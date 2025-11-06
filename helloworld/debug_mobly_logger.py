from mobly import base_test
from mobly import test_runner

class DebugTest(base_test.BaseTestClass):

    def setup_class(self):
        print("=== In setup_class ===")
        print("Available attributes:", [attr for attr in dir(self) if 'log' in attr.lower()])

    def test_check_logger(self):
        print("\n=== In test method ===")
        print("Available attributes:", [attr for attr in dir(self) if 'log' in attr.lower()])
        
        # Try to find the logger
        for attr in dir(self):
            if 'log' in attr.lower() and not attr.startswith('_'):
                print(f"\nFound: {attr}")
                try:
                    obj = getattr(self, attr)
                    print(f"  Type: {type(obj)}")
                    if callable(obj):
                        print("  Callable: Yes")
                except Exception as e:
                    print(f"  Error: {e}")

if __name__ == "__main__":
    test_runner.main()