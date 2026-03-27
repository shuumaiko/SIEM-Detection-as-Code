# Rule Architecture Review Notes

Date: 2026-03-19

This note consolidates the outputs from the working discussion about `rules/`, `deploy/`, `correlation`, `rule_type`, and source rule identifiers.

## 1. Current architectural reading

Based on `docs/architecture/`:

- `rules/` is the source of truth for detection content.
- detection logic should stay independent from vendor logs and SIEM implementation.
- hardcoded SIEM queries are acceptable as execution artifacts during the current transition phase.
- `artifacts/` is output, not long-term source content.

From current repository content:

- `rules/detections/...` contains atomic detection logic.
- `rules/analysts/...` contains correlation-style logic that references base detections.
- `deploy/splunk/.../*.deploy.yaml` currently contains `correlation`, which creates overlap between semantic rule logic and deploy-time content.

## 2. Main architecture issue identified

The main problem is not only naming. The bigger issue is that `deploy/splunk/...` is currently carrying semantic content that overlaps with `rules/`.

Observed conflict:

- `rules/analysts/...` already uses `correlation` as true detection logic.
- `deploy/splunk/...` also uses `correlation`, but for Splunk-specific supporting behavior.

This overloads the meaning of `correlation`.

## 3. Recommended semantic split

The recommended semantic split discussed in the chat is:

- `Detection Rule`: full detection logic, can stand independently.
- `Detection Base Rule`: a building block used mainly by analyst rules, not intended to stand alone as an alert.
- `Analyst Rule`: higher-level rule that contains correlation/aggregation/threshold/sequence logic.

Conclusion:

- `correlation` as real detection logic belongs under analyst rules.
- Splunk-specific support logic should not become a first-class semantic rule type.

## 4. Recommendation on naming: Analyst Rule vs Correlation Rule

Recommendation:

- use `Analyst Rule` as the main architectural term
- treat `correlation` as one technique that an analyst rule may use

Reasoning:

- `correlation rule` is narrower and too implementation-shaped
- `analyst rule` better captures business purpose
- this leaves room for future analyst-oriented logic that is not strictly correlation

Practical interpretation:

- folder/layer name: `rules/analysts/`
- semantic type: `rule_type: analyst`
- internal logic may still use a `correlation:` block where appropriate

## 5. Recommendation on `rule_type`

Adding `rule_type` was evaluated as a good idea.

Recommended values:

- `detection`
- `detection_base`
- `analyst`

Why:

- `level` should not be abused to distinguish standalone rules from building-block rules
- `rule_type` gives a clean semantic classifier
- `detection_base` can be excluded by default from direct deployment

Additional guidance:

- `Detection Rule` maps to `rule_type: detection`
- `Detection Base Rule` maps to `rule_type: detection_base`
- `Analyst Rule` maps to `rule_type: analyst`

## 6. Evaluation of the proposed "correlation overlay" concept

The discussion refined the meaning of the extra supporting layer:

- it is not execution metadata
- a rule that has this supporting layer must still pass through a separate execution layer to collect deployment metadata
- the supporting layer exists mainly to help analyst-facing alert display

After clarification, the final decision direction became:

- do not keep a separate `correlation_overlay` layer
- because this supporting behavior is currently only used for Splunk
- and other SIEMs do not consume it

## 7. Final direction for Splunk-only support logic

Final decision direction from the chat:

- remove the separate `correlation_overlay` idea
- push that supporting behavior into hardcoded SPL

Rationale:

- current use is Splunk-only
- creating a new domain layer for a single consumer would add complexity without enough benefit
- the repository docs already allow hardcoded SIEM-specific query artifacts as a transitional trade-off

Accepted trade-off:

- some analyst-support presentation logic will live in SPL
- this reduces abstraction purity
- but keeps the architecture simpler for now

Constraint that should remain clear:

- if the logic only improves Splunk alert display/grouping/context, it may live in hardcoded SPL
- if the logic changes the actual reusable detection semantics, it should move into `rules/analysts/`

Short rule of thumb:

- Splunk-only + display/supportive = hardcoded SPL
- reusable semantic correlation = analyst rule

## 8. Whether to keep upstream UUIDs from Sigma / ELK / YARA

Recommendation:

- keep the original upstream UUID when the internal rule is still substantially the same detection intent as the source rule
- create a new internal UUID when the rule has materially changed and has become a new detection object

Suggested usage:

- keep original `id` for near-direct derivatives
- keep `source_ref` or `source_rule_id` for traceability in all cases

Examples of when to keep the upstream UUID:

- field adaptation only
- metadata cleanup
- format conversion
- SIEM execution differences without changing core intent

Examples of when to create a new UUID:

- major detection logic changes
- combining multiple source rules into one
- converting a source rule into a building-block `detection_base`
- turning source content into a new analyst rule

Practical guidance agreed in the chat:

- `rules/detections` derived closely from Sigma/ELK/YARA: prefer keeping upstream UUID
- `detection_base` that is heavily internalized: consider new UUID
- `analyst` rules composed internally: always use a new UUID

## 9. Architectural summary

Current recommended direction after the discussion:

1. Keep the main semantic layers as:
   - `rules/detections`
   - `rules/analysts`

2. Introduce `rule_type` with:
   - `detection`
   - `detection_base`
   - `analyst`

3. Do not create a durable separate `correlation_overlay` abstraction for now.

4. Keep Splunk-only supportive display/grouping behavior inside hardcoded SPL.

5. Reserve `correlation` as a semantic detection construct mainly associated with analyst rules.

6. Keep upstream rule UUIDs only when the rule remains the same detection identity.

## 10. Proposed conventions to carry forward

- `rules/detections/` holds reusable atomic detection content.
- `rules/detections/` may contain both standalone detections and building-block detections, distinguished by `rule_type`.
- `rules/analysts/` holds higher-level semantic rules that use aggregation, thresholding, sequencing, or correlation-style logic.
- Splunk-only display/tuning/support behavior is allowed inside hardcoded SPL.
- Splunk-only support logic should not be elevated into a general semantic layer unless another SIEM needs the same abstraction.
- `level` should represent severity/operational meaning, not rule category or lifecycle role.

## 11. Open follow-up items

- define `rule_type` in schema and contributor guidance
- define whether `detection_base` is prevented from direct deployment by validation or only by convention
- decide whether `deploy/splunk/.../*.deploy.yaml` should remain as a file family or be replaced by another execution-file naming model
- document explicitly that some Splunk-specific analyst-support behavior is intentionally embedded in SPL as a controlled trade-off

