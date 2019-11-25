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
from absl import app, flags
from tqdm import tqdm
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import logging

FLAGS = flags.FLAGS

flags.DEFINE_float("download_chunk_size", 100, "Download chunk size in MB. Google API defaults to 100 MB.")
flags.DEFINE_bool("http_server_auth", False,
                  "Use the local server auth mode for the Google API. "
                  "This is more intuitive but is not possible on remote servers and so is disabled by default")

__CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
__SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
__CLIENT_SECRETS_FILE = os.path.join(__CURRENT_DIR, 'client_secrets.json')
__GDRIVE_TOKEN_FILE = os.path.join(__CURRENT_DIR, "gdrive_token.pickle")

# Disable verbose googleapiclient logging
logging.getLogger("googleapiclient").setLevel(logging.WARNING)


class GDriveHandler:
    """A python googleapiclient Google Drive wrapper for downloading the Oxford Radar RobotCar Dataset"""

    def __init__(self, download_dir):

        self.service = _get_drive_service()
        self.download_dir = os.path.expanduser(download_dir)
        # This access doesn't fail if FLAGS haven't been parsed
        self.download_chunk_size_bytes = int(FLAGS['download_chunk_size'].value * 1024 * 1024)

        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)
            if not os.path.isdir(self.download_dir):
                raise NotADirectoryError(f'Could not create download directory: {self.download_dir}')

    def download(self, file_id):

        # Set up download of file with fileID = <file_id>
        request = self.service.files().get_media(fileId=file_id, supportsTeamDrives=True)
        meta = self.service.files().get(fileId=file_id, supportsTeamDrives=True,
                                        fields='originalFilename, size').execute()
        filename = meta['originalFilename']
        output_path = os.path.join(self.download_dir, filename)
        with open(output_path, 'wb') as output_file:
            downloader = MediaIoBaseDownload(output_file, request, chunksize=self.download_chunk_size_bytes)

            # Perform download and stream data into output_file
            done = False
            desc = f"Downloading FileID {file_id} - {filename}"
            with tqdm(total=int(meta['size']), unit_scale=True, unit_divisor=1024, desc=desc) as pbar:
                while done is False:
                    status, done = downloader.next_chunk()
                    pbar.update(status.resumable_progress - pbar.n)

        return output_path


def _get_drive_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(__GDRIVE_TOKEN_FILE):
        with open(__GDRIVE_TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                __CLIENT_SECRETS_FILE, __SCOPES)
            if FLAGS['http_server_auth'].value:
                # Run local server based authentication
                creds = flow.run_local_server()
            else:
                # Run console based authentication
                creds = flow.run_console()
        # Save the credentials for the next run
        with open(__GDRIVE_TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


def main(unused_args):
    gdrive = GDriveHandler(download_dir='/tmp/radar_robotcar_dataset_test_download')


if __name__ == '__main__':
    app.run(main)
