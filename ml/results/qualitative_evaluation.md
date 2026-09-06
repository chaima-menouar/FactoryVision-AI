# PatchCore qualitative evaluation

This note records the first visual review of the hosted MVTec AD baseline.

## Bottle

Visualizations were reviewed for normal and defective samples, including contamination and small break defects.

Observed behavior:
- Normal examples showed no predicted defect mask.
- Contamination defects were localized around the true contaminated region.
- Small break defects were detected and localized at the correct part of the bottle rim.
- Anomaly maps were spatially broader than the final binary mask, which is expected from the score heatmap.

Conclusion: the bottle checkpoint is both quantitatively strong and qualitatively credible for the current baseline.

## Zipper

Zipper was reviewed because it had the weakest pixel-level F1 among the five selected categories.

Observed behavior:
- Normal examples did not show a predicted defect mask.
- `split_teeth` examples were localized around the actual damaged teeth.
- `squeezed_teeth` examples were localized around the true defect region.
- Some anomaly-map activation extends beyond the ground-truth defect, which helps explain the lower pixel-level F1 even when the main defect is correctly found.

Conclusion: the lower zipper pixel F1 is primarily a localization precision issue rather than a gross detection failure in the reviewed samples.

## Baseline decision

PatchCore is retained as the production-candidate baseline for the next engineering phase. Before wiring it into FastAPI, each selected checkpoint must pass an independent checkpoint-loading and single-image inference smoke test.

This decision does not claim that PatchCore is globally optimal. A second model such as EfficientAD can still be benchmarked later if deployment latency, artifact size, or localization quality requires it.
