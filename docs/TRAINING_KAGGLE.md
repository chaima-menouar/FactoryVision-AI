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

## Kaggle GPU compatibility

Kaggle can assign different GPUs. A Tesla P100 is a Pascal GPU with compute capability `sm_60`. Recent CUDA 12.8 PyTorch wheels may not contain `sm_60` kernels even when `torch.cuda.is_available()` returns `True`.

For a Kaggle Tesla P100, install the CUDA 12.6 wheel before training:

```bash
pip install --force-reinstall torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cu126
```

Restart the notebook kernel/session after replacing PyTorch, then verify that `torch.cuda.get_arch_list()` contains `sm_60`.

## Kaggle steps

1. Create a Kaggle notebook with Internet enabled for package installation.
2. Enable a GPU when available.
3. Attach the MVTec AD dataset.
4. Clone the FactoryVision AI repository into `/kaggle/working/FactoryVision-AI`.
5. If the assigned GPU is a Tesla P100 and the default PyTorch build reports an `sm_60` incompatibility, install the CUDA 12.6 PyTorch wheel shown above and restart the kernel/session.
6. Install the remaining hosted ML dependencies:

```bash
pip install -r /kaggle/working/FactoryVision-AI/ml/requirements-ml.txt
```

7. Point `--data-root` to the directory that directly contains category folders such as `bottle/`, `cable/`, etc. For the Kaggle `ipythonx/mvtec-ad` input used in our baseline, the resolved path is:

```text
/kaggle/input/datasets/ipythonx/mvtec-ad
```

8. Validate the directory:

```bash
python /kaggle/working/FactoryVision-AI/scripts/validate_mvtec.py /kaggle/input/datasets/ipythonx/mvtec-ad
```

9. Run the first baseline:

```bash
python /kaggle/working/FactoryVision-AI/ml/train_patchcore.py \
  --data-root /kaggle/input/datasets/ipythonx/mvtec-ad \
  --category bottle \
  --output-dir /kaggle/working/factoryvision-artifacts
```

10. Repeat only after the bottle experiment succeeds:

```bash
for category in cable metal_nut transistor zipper; do
  python /kaggle/working/FactoryVision-AI/ml/train_patchcore.py \
    --data-root /kaggle/input/datasets/ipythonx/mvtec-ad \
    --category "$category" \
    --output-dir /kaggle/working/factoryvision-artifacts
done
```

## What must be preserved after each run

Keep the generated Anomalib artifacts plus `metrics.json`. The evaluation gate for the next phase is based on **real** outputs only. We will compare image-level and pixel-level anomaly performance, inspect anomaly maps, study false positives/false negatives, and then decide whether PatchCore is sufficient or whether EfficientAD should be tested.

Do **not** commit dataset images or large model artifacts to GitHub. Download the selected artifact from Kaggle only after the baseline has been reviewed.

## Azure boundary

Azure is not required for this stage. We will not provision an Azure resource until the selected model, artifact format, API contract, persistence needs, and deployment footprint are known. Before that happens, current Azure free allowances and possible charges must be checked explicitly.