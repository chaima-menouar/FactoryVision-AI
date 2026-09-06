# Hosted training on Kaggle

FactoryVision AI deliberately keeps model training off personal machines. The first baseline uses **MVTec AD + PatchCore + Anomalib** in a free Kaggle notebook/session.

## Baseline scope

Run the first experiment on these categories:

- bottle
- cable
- metal_nut
- transistor
- zipper

Start with `bottle`. Do not run every category until the first run finishes cleanly and produces real metrics/artifacts.

## Kaggle steps

1. Create a Kaggle notebook with Internet enabled for package installation.
2. Use a GPU when available; PatchCore can also run on CPU because it builds a feature memory bank rather than performing conventional gradient training.
3. Clone the FactoryVision AI repository into the notebook session.
4. Install hosted ML dependencies:

```bash
pip install -r FactoryVision-AI/ml/requirements-ml.txt
```

5. MVTec AD can be supplied as a Kaggle dataset input. Point `--data-root` to the directory that directly contains category folders such as `bottle/`, `cable/`, etc. Anomalib can also prepare/download MVTec AD when its environment allows it.
6. Validate the directory when using an attached Kaggle copy:

```bash
python FactoryVision-AI/scripts/validate_mvtec.py /path/to/MVTecAD
```

7. Run the first baseline:

```bash
python FactoryVision-AI/ml/train_patchcore.py \
  --data-root /path/to/MVTecAD \
  --category bottle \
  --output-dir /kaggle/working/factoryvision-artifacts
```

8. Repeat only after the bottle experiment succeeds:

```bash
for category in cable metal_nut transistor zipper; do
  python FactoryVision-AI/ml/train_patchcore.py \
    --data-root /path/to/MVTecAD \
    --category "$category" \
    --output-dir /kaggle/working/factoryvision-artifacts
done
```

## What must be preserved after each run

Keep the generated Anomalib artifacts plus `metrics.json`. The evaluation gate for the next phase is based on **real** outputs only. We will compare image-level and pixel-level anomaly performance, inspect anomaly maps, study false positives/false negatives, and then decide whether PatchCore is sufficient or whether EfficientAD should be tested.

Do **not** commit dataset images or large model artifacts to GitHub. Download the selected artifact from Kaggle only after the baseline has been reviewed.

## Azure boundary

Azure is not required for this stage. We will not provision an Azure resource until the selected model, artifact format, API contract, persistence needs, and deployment footprint are known. Before that happens, current Azure free allowances and possible charges must be checked explicitly.
