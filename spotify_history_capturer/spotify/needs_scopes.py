from typing import Set


TOTAL_SCOPE_NEEDED = set()
''' Stores scopes that all objects decorated with `needs_scope` require. '''

def needs_scope(*scope):
    ''' Indicates that the decorated object that works with Spotify API requires scopes to work. Commonly used for functions that make Spotify API calls.
     :param scope: The scope that the access token is required to be granted.
     :see also: `TOTAL_SCOPE_NEEDED` '''
    if any(not isinstance(i, str) for i in scope):
        raise ValueError('All `scope` values must be strings. You have probably misused the decorator as `@needs_scope` and not `@needs_scope(...).`')
    def deco(obj):
        if hasattr(obj, 'needed_spotify_scope'):
            if isinstance(obj.needed_spotify_scope, Set): 
                obj.needed_spotify_scope.update(scope)
            else: 
                raise ValueError('needs_scope applied to a function that has "needed_spotify_scope" attribute of incorrect type.')
        else:
            obj.needed_spotify_scope = scope
        TOTAL_SCOPE_NEEDED.update(scope)
        return scope
    return deco