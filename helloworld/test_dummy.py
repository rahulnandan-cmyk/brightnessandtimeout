# /home/vvdn/sysfast-automation/src/test_dummy.py
from mobly import base_test, signals

class DummyMoblyTest(base_test.BaseTestClass):

    def setup_class(self):
        # Get all DummyDevice controllers
        self.dummy_devices = self.controllers.get('DummyDevice', [])
        for d in self.dummy_devices:
            print(f"Setup for {d['name']}")

    def test_dummy_action(self):
        for d in self.dummy_devices:
            print(f"Running dummy test on {d['name']}")
            if d['name'] == "Device2":
                raise signals.TestFailure(f"{d['name']} failed")

    def teardown_class(self):
        for d in self.dummy_devices:
            print(f"Tearing down {d['name']}")
