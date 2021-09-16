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
        pass

    def test_xrApply(self):
        pass


    def test_xrReplace(self):
        pass



    def tearDown(self):
        self.setNsMock.stop()
        self.getNsMock.stop()
        # os.remove(self._configFile)
