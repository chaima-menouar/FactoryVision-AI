# Data

Raw datasets are intentionally excluded from Git.

## Primary dataset — MVTec AD

FactoryVision AI starts with MVTec AD because it provides industrial object/texture images with normal training samples and anomalous test samples plus pixel-level ground truth for defect localization.

Recommended first categories for fast free-hosted experiments:

- bottle
- cable
- metal_nut
- transistor
- zipper

This mix covers objects with different shapes and defect patterns without forcing us to run all categories in the first iteration.

## Expected local/notebook layout

```text
data/raw/mvtec/
  bottle/
    train/good/
    test/good/
    test/<defect_type>/
    ground_truth/<defect_type>/
  ...
```

## Rules

1. Do not commit raw images to GitHub.
2. Do not commit trained checkpoints to GitHub.
3. Keep dataset licenses/terms with the training environment.
4. Training is performed on Kaggle/hosted notebooks, not on personal computers.
5. Add VisA or BTAD only after the MVTec baseline is reproducible.
