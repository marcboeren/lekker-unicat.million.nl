# Add projects by server and name, map to the project gid
# If the API key isn't stored yet, we will ask for it

# for server keys, you can choose between "localhost", "test", and "LIVE"

UNICAT_CONNECTIONS = {
    # "<server-key>.<project-name>": "<project-gid>",
    "LIVE.lekker": "22fddc08-b911-45a4-9107-7f5daff43393",
}

SFTP_CONNECTIONS = {
    # "<server-key>.<project-name>": "<user-name>",
    "LIVE.lekker": "ftp_million.nl",
}
