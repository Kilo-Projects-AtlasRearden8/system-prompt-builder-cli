"""Allow ``python -m system_prompt_builder``."""

import sys

from .cli import main

sys.exit(main())
