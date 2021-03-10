import unittest
import os
import tempfile
from unittest import mock

from lib.ztp_helper import ZtpHelpers

class MockZTPHelper:
    get_netns_path_method = 'lib.ztp_helper.ZtpHelpers.get_netns_path'
    setns_method = 'lib.ztp_helper.ZtpHelpers.setns'

    def mock_get_netns_path(*args, **kwargs):
        vrf_file = '/tmp/vrf'
        with open(vrf_file, 'w') as f:
            f.write('vrf')
        return vrf_file

    def mock__exec_shell_cmd(*args, **kwargs):
        return "output", None

class TestZtpHelpers(unittest.TestCase):
    def setUp(self):
        self.getNsMock = mock.patch(MockZTPHelper.get_netns_path_method, autospec=True, side_effect=MockZTPHelper.mock_get_netns_path)
        self.setNsMock = mock.patch(MockZTPHelper.setns_method,autospec=True, )
        self.setNsMock.start()
        self.getNsMock.start()

        self._configFile = '/tmp/base.config'
        self.helper = ZtpHelpers()
        self.helper.toggle_debug(False)


    def test_download_file(self):
        download_dir = 'test/'
        download_file = 'https://raw.githubusercontent.com/ios-xr/iosxr-ztp-python/master/lib/ztp_helper.py'
        ret = self.helper.download_file(file_url=download_file,
                         destination_folder=download_dir ,validate_server=False)
        self.assertEqual(ret['status'], 'success')
        os.remove(os.path.join(ret['folder'], ret['filename']))

    def test_xrcmd(self):
        pass

    def _resetConfigs(self):
        with open(self._configFile, 'w') as configFile:
            print("no hostname", file=configFile)

        result = self.helper.xrreplace(filename=self._configFile)
        self.assertEqual(result["status"], "success")
        os.remove(self._configFile)

    def test_adminCmd(self):
        cmd = None
        result = self.helper.admincmd(cmd)
        self.assertEqual(result, {"status": "error", "output": "No command specified"})

        cmd = 'Not a dictionary'
        result = self.helper.admincmd(cmd)
        self.assertEqual(result, {
            "status": "error",
            "output": "Dictionary expected as cmd argument, see method documentation"
        })

        # Sample admin cmd
        cmd = {'exec_cmd': 'show led location 0', 'prompt_response': ''}
        result = self.helper.admincmd(cmd)

        # Only need to check for success
        self.assertEqual(result['status'], "success")


        with open(self._configFile, 'w') as configFile:
            print("hostname new_hostname", file=configFile)

        result = self.helper.xrapply(filename=self._configFile, extra_auth=extra_auth)
        self.assertEqual(result["status"], "success")

        cmd = {'exec_cmd': 'show running-config', 'prompt_response': ''}
        result = self.helper.xrcmd(cmd)
        self.assertEqual(result["status"], "success")

        self.assertTrue("hostname new_hostname" in result["output"])

    def test_xrApply(self):
        print('Testing xrapply of hostname config')
        self._testHostnameConfig(self.helper.xrapply)
        print('Testing xrapply of hostname config with extra auth')
        self._testHostnameConfig(self.helper.xrapply, extra_auth=True)
        print('Testing xrapply of alias config with extra auth')
        self._testAliasConfig(self.helper.xrapply, extra_auth=True)


    def test_xrReplace(self):
        print('Testing xrapply of hostname config')
        self._testHostnameConfig(self.helper.xrapply)
        print('Testing xrapply of hostname config with extra auth')
        self._testHostnameConfig(self.helper.xrapply, extra_auth=True)
        print('Testing xrapply of alias config with extra auth')
        self._testAliasConfig(self.helper.xrreplace, extra_auth=True)



    def tearDown(self):
        self.setNsMock.stop()
        self.getNsMock.stop()
        # os.remove(self._configFile)
