"""Main entry point for Quinn package."""

import sys

if len(sys.argv) > 1 and sys.argv[1] == "web":
    from quinn.web import main

    main()
else:
    from quinn.cli import main

    main()
