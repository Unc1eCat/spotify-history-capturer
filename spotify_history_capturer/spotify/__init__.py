class conf:
    def __init__(self) -> None:
        raise RuntimeError('Do not instantiate.')

    CLIENT_ID = ...
    CLIENT_SECRET = ...

    URL_SPOTIFY_ACCOUNT = 'accounts.spotify.com'
    URL_SPOTIFY_API = 'api.spotify.com/v1'

