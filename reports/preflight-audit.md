# Pulmonary Rename collection preflight audit

Generated: 2026-09-16T18:42:10.335382-04:00

- Source: `/Users/chriselwell/Desktop/Rename` (read-only)
- Physical PNG files: 381
- Decodable files: 381
- Scored questions: 373
- Review-only sources: 8
- Source groups with multiple named variants: 47
- Low-resolution files (one dimension below 500 px): 73
- Quiz-safe border crops: 6
- Exact byte-identical duplicate groups: 0
- Provenance: all records are `third_party`; rights are unknown and the build is restricted to local study use.

## Modalities

- Angiography: 2
- CT: 68
- Clinical Image: 3
- Cytology: 2
- Diagram: 8
- Electron Microscopy: 4
- Gross Pathology: 45
- Gross pathology and histology: 1
- Histology: 104
- Immunohistochemistry: 6
- MRI: 1
- Ultrasound: 5
- X-ray: 126
- X-ray and CT: 5
- X-ray and pathology: 1

## Scored topic coverage

- Acute lung injury and edema: 12
- Airway and obstructive: 33
- Congenital and chest wall: 33
- Imaging patterns: 19
- Infection: 64
- Interstitial lung disease: 50
- Neoplasm: 47
- Normal anatomy: 22
- Pleural disease: 32
- Pulmonary pathology: 29
- Pulmonary vascular: 24
- Upper airway: 8

## Review-only decisions

- `Acute Asthma Attack` (src_133c8f085ec9): A near-normal chest radiograph cannot establish an acute asthma diagnosis by itself.
- `Appendicitis` (src_c12eecb01b3b): The filename and visible target do not establish a defensible pulmonary identification task.
- `Asthma` (src_9ea62021eef9): A normal or near-normal chest radiograph is not diagnostic of asthma.
- `Cystic fibrosis` (src_14b8edc63179): The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.
- `Cystic fibrosis` (src_7dfc37266c91): The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.
- `Normal` (src_69eae45a736d): The filename does not identify the organ, tissue compartment, or intended normal structure.
- `Pulmonary Infarct` (src_257ebb5b7dd8): Embedded labels state the tested diagnosis directly over medically meaningful tissue.
- `Pulmonary epithelial metaplasia` (src_38410f8d021a): The source label is ambiguous and the intended metaplastic process is not specified reliably.

## Transformation policy

All browser assets were losslessly re-encoded as PNG with metadata stripped. Transparency was composited onto a neutral background. Six answer-revealing captions or titles in non-diagnostic border space were removed with recorded source-relative crop coordinates. No image was stretched, upscaled, generatively reconstructed, or altered within diagnostic pixels.

## Ground-truth decision

The collection was descriptively renamed by the user before import. Keys were accepted only where the visible morphology was compatible during the complete contact-sheet review. Sources with insufficient, ambiguous, non-pulmonary, or answer-leaking evidence were withheld in the review queue.
