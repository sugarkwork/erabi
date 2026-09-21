"""CLI wrapper for the RC3.1 logic-recovery data build."""

from pathlib import Path
import sys

if __package__ in {None, ""}:
    # Make ``python scripts/build_rc3_1_logic_data.py`` work as well as the
    # module form, without changing the package's import boundaries.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.rc3_1_logic_data.build import main


if __name__ == "__main__":
    main()
