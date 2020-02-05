################################################################################
#
# Copyright (c) 2019 University of Oxford
# Authors:
#  Dan Barnes (dbarnes@robots.ox.ac.uk)
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to
# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
###############################################################################

from __future__ import division, print_function, absolute_import
import os.path
import subprocess
import os
import shutil
import platform
import requests
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

_ls = "=" * 100  # Logging separator
_current_dir = os.path.expanduser(os.path.abspath(os.path.dirname(__file__)))
_rrcd_registration_url = "https://ori.ox.ac.uk/datasets/radar-robotcar-dataset/registration"
_isWindows = platform.system() == "Windows"

_rclone_version = "v1.50.1"
_rclone_install_script_path = os.path.join(_current_dir, 'rclone', "install.sh")
_rclone_patched_install_script_name = "patched_rclone_install.sh"
_rclone_binary_name = "rclone.exe" if _isWindows else "rclone"
_rclone_rrcd_conf_unauthorised_name = "rclone_rrcd_unauthorised.conf"
_rclone_rrcd_conf_authorised_name = "rclone_rrcd.conf"
_rclone_rrcd_conf_drive_path = "rrcd_drive:"
_rclone_rrcd_conf_unauthorised_path = os.path.join(_current_dir, _rclone_rrcd_conf_unauthorised_name)


class GDriveHandler:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.bin, self.config = _initialise_dir_with_rclone(self.download_dir)
        self.call_args = [self.bin, "--config", self.config, "--drive-shared-with-me"]
        self.__authorise_if_needed()

    def download_filename(self, filename):
        output_path_raw = os.path.join(self.download_dir, filename)
        args = self.call_args + ["--progress", "copy", _rclone_rrcd_conf_drive_path + filename, self.download_dir]

        subprocess.check_call(args)
        if not os.path.isfile(output_path_raw):
            raise RuntimeError('Unexpected error in downloading file to: {}'.format(output_path_raw))

        output_path_zip = output_path_raw + ".zip"
        shutil.move(output_path_raw, output_path_zip)
        if not os.path.isfile(output_path_zip):
            raise RuntimeError('Unexpected error in adding zip extension to file: {}'.format(output_path_raw))

        return output_path_zip

    def __is_authorised(self):
        # We use the about call as a proxy for checking we are correctly authorised with Google Drive
        # I cannot find a better alternative than this at present
        args = self.call_args + ["about", _rclone_rrcd_conf_drive_path]
        res = subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # No error if we are correctly authorised
        return res == 0

    def __authorise_if_needed(self):
        if not self.__is_authorised():
            print("\n{}\nrclone config not authorised for downloads: {}".format(_ls, self.config))
            print("Authorisation needed. Please follow the rclone instructions to generate a read only Google Drive "
                  "token\nPlease use the Google Drive account you signed up with and were authorised for at: {}\n{}\n"
                  "".format(_rrcd_registration_url, _ls))
            args = self.call_args + ["config", "reconnect", _rclone_rrcd_conf_drive_path, "--auto-confirm"]
            res = subprocess.call(args)
            if res != 0:
                raise RuntimeError('Google Drive authentication failed: please run again')
            else:
                print("\nrclone authorised sucessfully")


def _initialise_dir_with_rclone(install_dir, create_dir_if_needed=True):
    ##########################################################################################
    # Create directory if necessary
    ##########################################################################################
    if not os.path.isdir(install_dir):
        if create_dir_if_needed:
            os.makedirs(install_dir)
        else:
            raise NotADirectoryError('install_dir does not exist and create_dir_if_needed is False: '
                                     '{}'.format(install_dir))

    ##########################################################################################
    # Run modified rclone install script with download folder and rclone version
    ##########################################################################################
    print("{}\nInitialising rclone to: {}\n{}".format(_ls, install_dir, _ls))

    if not _isWindows:
        return_code = subprocess.call(['bash', _rclone_install_script_path, install_dir, _rclone_version],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if return_code == 0:
            print('rclone install script: exited without problems')
        elif return_code == 1:
            raise RuntimeError(
                'rclone install script: parameters not supported were used or some unexpected error occurred')
        elif return_code == 2:
            raise RuntimeError('rclone install script: OS not supported by this script')
        elif return_code == 3:
            print('rclone install script: installed version of rclone is already at requested version: '
                  '{}'.format(_rclone_version))
        elif return_code == 4:
            raise RuntimeError('rclone install script: supported unzip tools are not available')
        else:
            raise RuntimeError('rclone install script: unexpected return code {}'.format(return_code))
    else:

        # If rclone exists, check the version is correct
        download_rclone_path = os.path.join(install_dir, _rclone_binary_name)
        rclone_exists = os.path.isfile(download_rclone_path)
        if rclone_exists:
            res = subprocess.check_output([download_rclone_path, "version"]).decode('utf-8').splitlines()[0]
            correct_version = _rclone_version in res

        if (not rclone_exists) or (not correct_version):
            windows_binary_download_url = \
                "https://downloads.rclone.org/{}/rclone-{}-windows-amd64.zip".format(_rclone_version, _rclone_version)
            print("Downloading rclone (Windows):\nSource: {}\nDest  : {}".format(windows_binary_download_url,
                                                                                 download_rclone_path))
            # Download and unzip
            rclone_versioned_download_folder = os.path.splitext(os.path.split(windows_binary_download_url)[1])[0]
            response = requests.get(windows_binary_download_url)
            with NamedTemporaryFile('wb') as tmpfile:
                tmpfile.file.write(response.content)
                ZipFile(tmpfile.name).extractall(install_dir)

            # Copy to correct location (leave original download for debugging)
            rclone_bin_copy_src = os.path.join(install_dir, rclone_versioned_download_folder, _rclone_binary_name)
            rclone_bin_copy_dest = os.path.join(install_dir, _rclone_binary_name)
            shutil.copyfile(rclone_bin_copy_src, rclone_bin_copy_dest)

    ##########################################################################################
    # Check the rclone binary is found as expected
    ##########################################################################################
    rclone_path = os.path.join(install_dir, _rclone_binary_name)
    if not os.path.isfile(rclone_path):
        raise FileNotFoundError('Unexpected error. rclone binary not found after running install script: '
                                '{}'.format(rclone_path))
    print("\n{}\nrclone binary at : {}\n{}".format(_ls, rclone_path, _ls))

    ##########################################################################################
    # Copy template authorisation if needed
    ##########################################################################################
    rclone_authorised_config_path = os.path.join(install_dir, _rclone_rrcd_conf_authorised_name)
    if not os.path.isfile(rclone_authorised_config_path):
        # Need to copy template rclone config
        if not os.path.isfile(_rclone_rrcd_conf_unauthorised_path):
            raise FileNotFoundError('Unexpected error. Could not find template rclone configuration: '
                                    '{}'.format(_rclone_rrcd_conf_unauthorised_path))
        shutil.copyfile(_rclone_rrcd_conf_unauthorised_path, rclone_authorised_config_path)

    # Double check that the copied config exists
    if not os.path.isfile(rclone_authorised_config_path):
        raise FileNotFoundError('Unexpected error. Could not find rclone configuration after copying: '
                                '{}'.format(rclone_authorised_config_path))

    print("\n{}\nrclone config at: {}\n{}".format(_ls, rclone_authorised_config_path, _ls))

    return rclone_path, rclone_authorised_config_path


if __name__ == '__main__':
    gdrive = GDriveHandler(download_dir='/tmp/radar_robotcar_dataset_test_download')
    gdrive.download_filename("2019-01-15-14-24-38-radar-oxford-10k_Bumblebee_XB3_Visual_Odometry")
