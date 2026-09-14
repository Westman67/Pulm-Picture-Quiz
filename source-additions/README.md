# Pulmonary picture additions

This is the quiz project's self-contained supplemental source library.

- `originals/`: 37 supplemental source images, including the user-supplied asbestos-related pleural-plaque, Coccidioides, neonatal BPD, and acute ARDS specimens
- `variants/`: deterministic quiz-safe crops or masks for the base supplement
- `promotions/originals/`: six preserved copies of user-approved RLS review sources
- `promotions/variants/`: six project-local quiz-safe scored derivatives
- `picture_quiz_supplemental_manifest.json`: base supplemental manifest
- `picture_quiz_review_promotions.json`: review-promotion manifest
- `source_media/`: source videos used for fixed-frame extraction

The external `Pulmonary Picture Quiz Additions` folder and canonical `Picture Quiz` RLS library are not required to supply supplemental photos at runtime. The RLS library remains the read-only upstream source for regeneration and provenance. Local-only educational images must not be redistributed.
