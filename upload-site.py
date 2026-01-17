import os
from getpass import getpass
from pathlib import Path

import ftputil
import keyring

HOSTNAME = "srv040075.webreus.net"
USERNAME = "ftp_million.nl"
FOLDER = "upload-generated-site"

ftp_password = keyring.get_password("sftp.password", "lekker.million.nl")
if not ftp_password:
    ftp_password = getpass("Enter SFTP password for 'lekker.million.nl': ")
    keyring.set_password("sftp.password", "lekker.million.nl", ftp_password)

folder = Path(FOLDER)
if not Path(folder).is_absolute():
    folder = Path(Path.cwd(), folder)
folder = folder.resolve()

print()
print("Uploading files and images")
print()
with ftputil.FTPHost(HOSTNAME, USERNAME, ftp_password) as host:
    host.chdir("lekker")
    for root, dirs, files in os.walk(folder):
        remote_folder = root[len(str(folder)) + 1 :]
        if remote_folder:
            host.makedirs(remote_folder, exist_ok=True)
        print(remote_folder, end="", flush=True)
        for file in files:
            local_file = f"{root}/{file}"
            remote_file = f"{remote_folder}/{file}" if remote_folder else file
            # print(local_file, "--->", remote_file)
            host.upload_if_newer(local_file, remote_file)
            print(".", end="", flush=True)
        print(f" {len(files)} {'file' if len(files) == 1 else 'files'}")
print(flush=True)
