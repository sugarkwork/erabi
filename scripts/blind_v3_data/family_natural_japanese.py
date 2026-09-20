"""Family 4: natural_japanese (30 pairs, 60 cases) - Blind v3
Distribution: K=2 (10 pairs), K=3 (5 pairs), K=4 (10 pairs), K=6 (5 pairs)
Prefix: rc2b3_nat_
"""

from typing import Any, Dict, List, Tuple
from blind_v2_data.family_natural_japanese import get_natural_japanese_pairs as get_v2_nat


def get_natural_japanese_pairs() -> List[Dict[str, Any]]:
    v2_pairs = get_v2_nat()
    v3_pairs = []
    for c in v2_pairs:
        c_new = dict(c)
        c_new["id"] = c["id"].replace("rc2b_nat_", "rc2b3_nat_")
        c_new["group_id"] = c["group_id"].replace("rc2b_nat_", "rc2b3_nat_")
        v3_pairs.append(c_new)
    return v3_pairs
