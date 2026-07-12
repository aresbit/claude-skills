# Geometry Iteration

Use this reference when building or debugging a 3D model through repeated render-inspect-revise cycles. CAD design is inherently iterative — treat every model as a draft that improves through structured refinement.

## Loop

1. Produce a minimal renderable model.
2. Generate evidence from multiple angles: render at least 3 orthogonal views (front/side/top) plus an isometric view, plus any section cuts or dimension annotations needed.
3. Compare the evidence against the brief using both qualitative (visual) and quantitative (numerical) checks.
4. State the specific defect with precise spatial language (e.g., "mounting hole offset +2mm in X" not "it looks wrong").
5. Apply the smallest plausible fix — change one parameter or operation.
6. Validate parameter consistency before re-rendering (e.g., inner < outer, wall > 0, cutout smaller than parent body).
7. Repeat until the remaining uncertainty is minor and explicitly acknowledged.

## Two Modalities of Evidence

Always gather both types of evidence — they catch different classes of errors:

### Qualitative (Visual)
- Multi-view renders: front, side, top, isometric as minimum
- Silhouette and proportion checks
- Symmetry and alignment verification
- Feature relationship checks (does hole A align with tab B?)

### Quantitative (Numerical)
- Bounding box dimensions
- Critical measurements against the design brief
- Clearance distances between mating parts
- Parameter relationship validation (are all constraints self-consistent?)

## What To Inspect

### Global form

- Overall proportions
- Symmetry and centering
- Orientation of major features
- Whether the silhouette matches the intended object

### Functional geometry

- Hole diameter and placement
- Wall thickness
- Slot widths and insertion paths
- Clearances for lids, fasteners, or mating parts
- Contact surfaces and support points

### Parameter consistency

- Inner radius < outer radius (for concentric features)
- Cutout dimensions < parent body dimensions
- Wall thickness > 0 after all boolean operations
- No zero-thickness or coplanar geometry at boolean boundaries
- Clearance values are positive and appropriate for the fabrication method

### Fabrication risk

- Thin or fragile members
- Unsupported bridges and overhangs
- Internal voids that cannot be cleaned or printed
- Sharp internal corners where a radius is likely needed

## How To Diagnose Problems

- If the whole part looks wrong, inspect coordinate system choices and base dimensions first.
- If one feature drifts, inspect local transforms and subtraction volumes.
- If symmetry is off, replace duplicated magic numbers with mirrored parameters.
- If exported meshes fail, simplify booleans and check for coplanar or zero-thickness geometry.
- If the part is hard to revise, refactor repeated dimensions into named parameters before continuing.
- If parameters are contradictory, the model may still render but will produce invalid geometry — validate constraints before debugging the visual output.
- If a user provides verbal feedback ("make the base wider"), localize the affected feature before changing any parameter.

## Multi-View Rendering

When generating evidence, produce enough views to eliminate ambiguity:

| Minimum set | When to add more |
|---|---|
| Front, side, top, isometric | Asymmetric features, internal geometry, mating interfaces |

- Use section cuts to expose internal voids, channels, and fit relationships.
- For parts with mating surfaces, include a view showing both parts in position.
- Annotate key dimensions directly on renders when the environment supports it.
- Rotate the isometric view to show the most geometrically dense corner.

## Modeling Style

- Use named parameters for every critical dimension.
- Group related operations into small modules or functions.
- Keep boolean operands readable and spatially local.
- Comment only where spatial intent is not obvious from the code.
- Prefer deterministic geometry over clever compact code.
- Validate parameter relationships at the top of the model file before any geometry operations.

## OpenSCAD Notes

- Start from primitives and boolean composition.
- Keep `difference()`, `union()`, and `intersection()` blocks visually clean.
- Avoid burying key dimensions inside nested transforms.
- When debugging, isolate one body or subtraction volume at a time.
- Use `assert()` to enforce parameter constraints (e.g., `assert(inner_r < outer_r)`).

## build123d Notes

- Separate sketch definition from 3D feature creation.
- Name workplanes and construction geometry clearly.
- Treat fillets and chamfers as late-stage operations.
- Use helper functions when a feature repeats with stable intent.
- Validate sketch constraints before extruding — a bad sketch propagates errors through the entire model.

## Response Pattern

When reporting progress to the user, keep it concrete:

- What changed
- What evidence you used to verify it (both qualitative and quantitative)
- What remains uncertain

Do not claim a fit-critical model is correct unless it has been verified by multi-view render evidence, explicit dimension checks, and parameter consistency validation — or user-provided measurements.
