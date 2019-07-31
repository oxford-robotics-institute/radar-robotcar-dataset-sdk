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
from absl import app, logging, flags
import os.path
import platform
import subprocess
from google_drive_downloader import GoogleDriveDownloader as gdd
import tempfile
import sys
import pexpect

FLAGS = flags.FLAGS
flags.DEFINE_string("gdrive_binary_name", None, "GDrive binary name")

# We use this forked gdrive which has Team Drive support
# https://github.com/petrpulc/gdrive
# Generate the below list with any gdrive instance with the command:
# gdrive list  --query " '12GSQhLLdKDdKzq_a-7WOrip5HnFmm1v9' in parents"
gdrive_binary_list_raw = """Id                                  Name                     Type   Size     Created
1iIjBty1FKxdGvyc4GATngwgbzQdPYz2p   gdrive-linux-x64         bin    4.8 MB   2018-11-01 19:33:47
1gXMutwGQ-HJ0zKwOKlMqEKt3197UhYn8   gdrive-linux-386         bin    4.2 MB   2018-11-01 19:32:59
1LkAchi-D9KzvRcGWVcmSJl6c8PG9QWzS   gdrive-windows-x64.exe   bin    4.7 MB   2018-11-01 19:34:29
1qBuNl46cSqYsbNBgNYAgH74NFhD11epX   gdrive-windows-386.exe   bin    4.2 MB   2018-11-01 19:34:26
1pU9HVjiNvxaXyRtaX7hltyjyYF4glonT   gdrive-solaris-x64       bin    4.7 MB   2018-11-01 19:34:24
13OZeLVUQJBC8WdMEtsKPR8eVVU1ZZ4AB   gdrive-plan9-x64         bin    4.5 MB   2018-11-01 19:34:22
1smW7u9JANDGAZxQZjgWOj0Qr1Kj3h0P2   gdrive-plan9-386         bin    4.0 MB   2018-11-01 19:34:20
1GL18Ety5Le8IpNwRKO1iZg1YWV_cCWUN   gdrive-osx-x64           bin    5.2 MB   2018-11-01 19:34:17
1dGh5g88D2jq-KeVOMcbAYpJkd20mUBDi   gdrive-osx-386           bin    4.7 MB   2018-11-01 19:34:04
1sLp4DRDKkyaKoUcz03UGjXR1zYdJb4-N   gdrive-openbsd-x64       bin    4.8 MB   2018-11-01 19:34:01
1wlzUqpzsE9XS4rK2EVJ1C2WiWxL79QgM   gdrive-openbsd-arm       bin    4.4 MB   2018-11-01 19:33:59
19CNffIDUygHWQWw6hP7tLECeqzfmaCwU   gdrive-openbsd-386       bin    4.2 MB   2018-11-01 19:33:57
1xleqVF8HlkLp_el8-CS30g23Pta-IyUj   gdrive-netbsd-x64        bin    4.8 MB   2018-11-01 19:33:54
14WbEoaHiPDNFi7dgecav6XrFAYZAYBME   gdrive-netbsd-arm        bin    4.4 MB   2018-11-01 19:33:52
1Ev7sgDmYZoZb_krBd95fej_vaqYAIqtK   gdrive-netbsd-386        bin    4.2 MB   2018-11-01 19:33:49
1SMrO7Kh3BjetpL2nBykgtjedVICZxJtJ   gdrive-linux-rpi         bin    4.4 MB   2018-11-01 19:33:45
1Ul1NBy7S2fOEomF0pLY1RmmcLeYwsWFA   gdrive-linux-ppc64le     bin    5.0 MB   2018-11-01 19:33:43
1kafdBT0nZllg2joivg_VQItTLD3mH_Cg   gdrive-linux-ppc64       bin    5.0 MB   2018-11-01 19:33:39
1xazXLlduU1QSJYMU8Ch_WfIbkmrHGXct   gdrive-linux-mips64le    bin    5.7 MB   2018-11-01 19:33:37
1sFHrFwVhR6su1iR39j5LR52loA9nA228   gdrive-linux-mips64      bin    5.7 MB   2018-11-01 19:33:34
1N-26SYJ5IQ8hXbc_DTJ-tYMaoOpvmtKl   gdrive-linux-arm64       bin    4.9 MB   2018-11-01 19:33:31
1enssEMj7FXEZUkbu8AVabOeKRmWt99wa   gdrive-linux-arm         bin    4.4 MB   2018-11-01 19:33:29
1klUCs5B6uMJ-WoZFjq6S0kphM1eRAU0F   gdrive-freebsd-x64       bin    4.8 MB   2018-11-01 19:32:56
1foJs2QP6Tv7EYyqvd5gnDbllxuwPn4aF   gdrive-freebsd-arm       bin    4.4 MB   2018-11-01 19:32:51
1GXmTKyz4nXCSnX15CjmM7d3LzMBmBzdV   gdrive-freebsd-386       bin    4.2 MB   2018-11-01 19:32:49
1zOWRZAnIHgaSXQpiqdirRc8q4gU8mdeg   gdrive-dragonfly-x64     bin    4.8 MB   2018-11-01 19:32:47"""
gdrive_binary_list = [l.split() for l in gdrive_binary_list_raw.splitlines()[1:]]


class GDriveHandler:
    def __init__(self):
        self.bin = check_gdrive_exists_or_download(True)

    def info(self, id):
        args = [self.bin, 'info', id]
        resp = subprocess.check_output(args)
        return resp

    def download(self, id, destination, timeout=0):
        args = [self.bin, 'download', "--timeout", str(timeout), "--force", "--path", destination, id]
        res = subprocess.check_output(args)
        output_file = res.decode().splitlines()[0].split()[-1]
        return output_file

    def upload(self, filepath, folder_id, timeout=0):
        args = [self.bin, 'upload', "--parent", folder_id, "--timeout", str(timeout), filepath]
        subprocess.check_call(args)


def check_gdrive_exists_or_download(check_authorised=True, download_gdrive_dir=tempfile.gettempdir()):
    # This is not very robust but covers the main systems

    if (not FLAGS.is_parsed()) or (FLAGS.gdrive_binary_name is None):
        system = platform.system().lower()
        if system == "darwin":
            system = "osx"
        processor_string_lookup = {
            "i386": "386",
            'x86_64': "x64",
        }
        processor_str = processor_string_lookup[platform.processor()]
        gdrive_binary_name_search = "-".join(["gdrive", system, processor_str])
    else:
        gdrive_binary_name_search = FLAGS.gdrive_binary_name

    try:
        candidate_binaries = [g for g in gdrive_binary_list if g[1] == gdrive_binary_name_search]
        gdrive_binary = candidate_binaries[0]
        gdrive_binary_name = gdrive_binary[1]
    except KeyError or IndexError:
        print(f"Could not automatically determine the correct gdrive binary string for system: {platform.platform()}")
        print(f"Please feed the correct Name of the binaries from below as flag --gdrive_binary_name")
        print(gdrive_binary_list_raw)
        raise LookupError

    paths = os.environ['PATH'].split(':') + ['/usr/local/bin', download_gdrive_dir, '.']
    gdrive_binary_paths = [f'{path}/{gdrive_binary_name}' for path in paths]
    found = [os.path.isfile(gp) for gp in gdrive_binary_paths]
    if any(found):
        gdrive_binary_path = [p for p, f in zip(gdrive_binary_paths, found) if f][0]
    else:
        gdrive_binary_path = f"/{download_gdrive_dir}/{gdrive_binary[1]}"
        gdd.download_file_from_google_drive(file_id=gdrive_binary[0],
                                            dest_path=gdrive_binary_path)
        subprocess.check_output(["chmod", "+x", gdrive_binary_path])

    print(f"Using GDrive binary: {gdrive_binary_path}")
    sys.stdout.flush()
    if check_authorised:
        verify_gdrive_authorised(gdrive_binary_path)
    return gdrive_binary_path


def verify_gdrive_authorised(gdrive_binary_path):
    verification_code = "Enter verification code:"
    no_verification_code = "Max upload size:"
    child = pexpect.spawn(gdrive_binary_path, ["about"])
    returns = [verification_code, no_verification_code, pexpect.EOF]
    index = child.expect(returns)
    if returns[index] == pexpect.EOF:
        raise RuntimeError(f'Unexpected GDrive banch')
    elif returns[index] == no_verification_code:
        return
    else:
        print("\n" + child.before.decode())
        print(child.after.decode())
        child.sendline(input())
        returns = [no_verification_code, pexpect.EOF]
        index = child.expect(returns)
        if returns[index] == pexpect.EOF:
            raise RuntimeError(f'Unexpected GDrive banch')
        elif returns[index] == no_verification_code:
            print("\nGDrive Authorised\n")
            return

def main(unused_args):
    check_gdrive_exists_or_download(True)
    gdrive = GDriveHandler()


if __name__ == '__main__':
    app.run(main)
