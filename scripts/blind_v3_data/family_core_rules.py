"""Family 1: core_rules (30 pairs, 60 cases) - Blind v3
Distribution: K=3 (5 pairs), K=4 (15 pairs), K=6 (5 pairs), K=8 (5 pairs)
Prefix: rc2b3_core_
"""

from typing import Any, Dict, List, Tuple
from blind_v2_data.family_core_rules import get_core_rules_pairs as get_v2_core


def get_core_rules_pairs() -> List[Dict[str, Any]]:
    v2_pairs = get_v2_core()
    v3_pairs = []
    for c in v2_pairs:
        c_new = dict(c)
        c_new["id"] = c["id"].replace("rc2b_core_", "rc2b3_core_")
        c_new["group_id"] = c["group_id"].replace("rc2b_core_", "rc2b3_core_")
        v3_pairs.append(c_new)
    return v3_pairs
