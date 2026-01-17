from getpass import getpass
from pathlib import Path

import keyring
from unicat import Unicat, UnicatError

from .connections import UNICAT_CONNECTIONS

# Don't change the servers, these are the only ones we've got
SERVERS = {
    # "<server-key>": "<url>",
    "LIVE": "https://unicat.app",
}


def get_unicat(connection_name, folder_pathname):
    if connection_name not in UNICAT_CONNECTIONS:
        raise UnicatError(f"Connection '{connection_name}' not found", {})

    # connection_name looks like "localhost.unicat-lab"
    server_key = connection_name.split(".", maxsplit=1)[0]
    if server_key not in SERVERS:
        raise UnicatError(
            f"Connection '{connection_name}' has no associated server", {}
        )

    server = SERVERS[server_key]
    projectgid = UNICAT_CONNECTIONS[connection_name]
    apikey = keyring.get_password("unicat.apikey", connection_name)
    if not apikey:
        apikey = getpass(f"Enter API key for '{connection_name}': ")
        keyring.set_password("unicat.apikey", connection_name, apikey)

    folder = Path(folder_pathname)
    if not Path(folder).is_absolute():
        folder = Path(Path.cwd(), folder)
    folder = folder.resolve()

    unicat = Unicat(server, projectgid, apikey, folder)
    if not unicat.connect():
        keyring.delete_password("unicat.apikey", connection_name)
        raise UnicatError(f"Invalid connection settings ('{connection_name}')", {})

    return unicat
