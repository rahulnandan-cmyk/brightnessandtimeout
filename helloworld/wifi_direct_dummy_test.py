import time
from mobly import base_test
from mobly import test_runner
from mobly import asserts

class WifiDirectDummyTest(base_test.BaseTestClass):
    """Simulated Wi-Fi Direct Test without real devices."""

    def setup_class(self):
        # Simulate controller registration
        self.ads = ["DummyDevice1", "DummyDevice2"]
        self.log.info(f"Registered devices: {self.ads}")

    def _init_wifi_p2p(self, device):
        self.log.info(f"[{device}] Initializing Wi-Fi P2P...")
        time.sleep(1)
        return True

    def test_wifi_direct_connect(self):
        group_owner, client = self.ads

        # Simulate Wi-Fi Direct init
        assert self._init_wifi_p2p(group_owner)
        assert self._init_wifi_p2p(client)

        # Simulate creating group
        self.log.info(f"[{group_owner}] Creating Wi-Fi Direct group...")
        time.sleep(1)
        success_owner = True

        # Simulate client joining
        self.log.info(f"[{client}] Connecting to group...")
        time.sleep(1)
        success_client = True

        # Assertions
        asserts.assert_true(success_owner, "Group creation failed!")
        asserts.assert_true(success_client, "Client connection failed!")

        self.log.info("Wi-Fi Direct simulation successful ✅")

    def teardown_test(self):
        self.log.info("Cleaning up simulated devices...")

if __name__ == "__main__":
    test_runner.main()
