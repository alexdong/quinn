# Set default encoding
import locale
import os
import sys

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# Enable better error messages in development
if os.environ.get("DEBUG"):
    import pdb

    sys.excepthook = lambda *args: pdb.post_mortem()  # noqa: ARG005
