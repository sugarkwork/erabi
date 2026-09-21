# ERABI RC3.1 Logic Recovery Data Report

Build: `rc3.1-logic-recovery-v2`

Blind v5 was audited as historical data only; no Blind v5 generator, text, or numeric state was imported.

## Train / dev / calibration

- Records: 2400 (1200 pairs)
- Split records: {'train': 1920, 'dev': 240, 'calibration': 240}
- Token max/avg: 133 / 121.43
- Semantic, exact/normalized/fuzzy historical-overlap, split-isolation, balance, and token audits: PASS

## Logic Bridge

- Records: 480 (240 contrastive pairs)
- Token max/avg: 142 / 125.55
- Semantic, exact/normalized/fuzzy historical-overlap, train-isolation, balance, and token audits: PASS

## Frozen-boundary note

Existing RC3 artifacts and Blind v5 were not modified. GPU training, calibration, ONNX export, and Blind v6 were not run.

