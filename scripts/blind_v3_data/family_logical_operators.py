"""Family 2: logical_operators (30 pairs, 60 cases) - Blind v3
Distribution: K=2 (15 pairs), K=3 (10 pairs), K=4 (5 pairs)
Prefix: rc2b3_op_
"""

from typing import Any, Dict, List, Tuple
from blind_v2_data.family_logical_operators import get_logical_operators_pairs as get_v2_op


def get_logical_operators_pairs() -> List[Dict[str, Any]]:
    v2_pairs = get_v2_op()
    v3_pairs = []
    for c in v2_pairs:
        c_new = dict(c)
        c_new["id"] = c["id"].replace("rc2b_op_", "rc2b3_op_")
        c_new["group_id"] = c["group_id"].replace("rc2b_op_", "rc2b3_op_")
        v3_pairs.append(c_new)
    return v3_pairs
