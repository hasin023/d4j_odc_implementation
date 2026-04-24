"""Interactive REPL-based CLI for the D4J ODC Pipeline.

Launch with: python -m d4j_odc_pipeline  (no arguments)
"""

from __future__ import annotations


def launch_repl() -> int:
    """Entry point for the interactive REPL session."""
    from .app import ODCApp
    return ODCApp().run()
