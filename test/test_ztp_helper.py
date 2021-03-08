import unittest
import os
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

class TestZtpHelpers(unittest.TestCase):
    @mock.patch(MockZTPHelper.get_netns_path_method, side_effect=MockZTPHelper.mock_get_netns_path)
    @mock.patch(MockZTPHelper.setns_method)
    def test_download_file(self, mock_get_netns_path, mock_setns):
        zh = ZtpHelpers()
        download_dir = 'test/'
        dwnld_file = 'https://raw.githubusercontent.com/ios-xr/iosxr-ztp-python/master/lib/ztp_helper.py'
        ret = zh.download_file(file_url=dwnld_file,
                         destination_folder=download_dir ,validate_server=False)
        self.assertEqual(ret['status'], 'success')
        os.remove(os.path.join(ret['folder'], ret['filename']))
        print(ret)