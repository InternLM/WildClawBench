"""Claude Code subscription bridge for wildclawbench.

Routes Anthropic API traffic through the user's Claude Code OAuth subscription
instead of an API key, by:

  1. Reading OAuth credentials from macOS Keychain (or the credentials file).
  2. Exposing an Anthropic-compatible HTTP server (``/v1/messages``) that
     forwards requests upstream with the OAuth bearer token + required
     ``anthropic-beta: oauth-2025-04-20`` header + ``You are Claude Code``
     system prefix.

See ``docs/CLAUDE_CODE_BRIDGE.md`` for setup, ToS caveats, and integration
with the existing aider/litellm pipeline.
"""

from .credentials import (
    CredentialProvider,
    CredentialsError,
    MultiAccountCredentialProvider,
    OAuthCredentials,
    load_account_pool,
    load_credentials,
    refresh_credentials,
)
from .errors import (
    ClassifiedError,
    ErrorKind,
    classify_anthropic_error,
    extract_retry_after,
)

__all__ = [
    "ClassifiedError",
    "CredentialProvider",
    "CredentialsError",
    "ErrorKind",
    "MultiAccountCredentialProvider",
    "OAuthCredentials",
    "classify_anthropic_error",
    "extract_retry_after",
    "load_account_pool",
    "load_credentials",
    "refresh_credentials",
]
