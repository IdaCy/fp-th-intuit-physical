# methods note

## benchmark definition

The benchmark starts from the public INTUIT single-capability human battery and keeps only templates whose required metadata components are physical and not social.

That filter retains 8 templates:
- `01.1.0.0.a`
- `01.1.0.0.b`
- `03.1.0.0.a`
- `03.1.0.0.b`
- `05.1.0.0.a`
- `05.1.0.0.b`
- `12.1.0.0.a`
- `12.1.0.0.b`

Each retained template has six counterbalanced human instantiations, giving 48 item instances.

## human timing methodology

Human timing comes from `paper_results/human_data_single_clean.csv` in the public OSF archive.

Filtering follows the public INTUIT notebook:
- keep rows with `Display == "Trial"` and `Screen == "vignette"`
- exclude participants who fail the attention check
- exclude participants whose median reaction time is below 20 seconds
- exclude trials below 5 seconds from timing and accuracy summaries

Main time-horizon axis:
- median human reaction time over all valid attempts for each item instance

Sensitivity axis:
- median human reaction time over correct valid attempts only

The two timing axes are close on this subset:
- correlation between item medians: `0.952`
- median absolute difference: `0.45s`

Human summary on the final subset:
- 53 included participants
- mean item-level human accuracy: `0.895`
- median item-level median reaction time: `26.57s`

## model evaluation

Prompting is single-call across all conditions:
- `no_cot`: answer with a single digit `1` to `4`
- `cot`: brief reasoning is allowed, but the response must end with `Final answer: <digit>`
- `repeat`: the vignette is repeated once before the same strict one-digit output instruction

Shared rules:
- no examples
- no tool use
- no multi-turn repair

Decoding settings:
- `gpt-5-mini` no-CoT: `responses` API with `reasoning.effort = minimal`
- `gpt-5.4` no-CoT: `responses` API with `reasoning.effort = none`
- `gpt-5.4` CoT: `responses` API with `reasoning.effort = medium`
- `gpt-5.4` repeat: `responses` API with `reasoning.effort = none`
- `gpt-4.1` no-CoT: `responses` API with default non-reasoning settings
- output cap: 32 tokens for `no_cot` and `repeat`, 512 tokens for `cot`

If a model output does not contain a digit from `1` to `4`, the runner retries once with a stricter format wrapper for the active condition. The final `gpt-5.4` CoT and repeat runs completed with zero parse failures.

Final model summary:

| model | condition | accuracy |
| --- | --- | ---: |
| `gpt-5-mini` | `no_cot` | 0.854 |
| `gpt-5.4` | `no_cot` | 0.917 |
| `gpt-5.4` | `cot` | 0.958 |
| `gpt-5.4` | `repeat` | 0.958 |
| `gpt-4.1` | `no_cot` | 0.917 |

## analysis

Primary outcome:
- model accuracy by item instance

Summary views:
- overall accuracy with Wilson 95% intervals
- accuracy by quartile bin of median human time
- accuracy by physical context
- comparisons by model and prompting condition

## cost

Actual API spend recorded in `private/cost_tracking.md`:
- original phase 1 total: `$0.1269`
- phase 2 additions: `$0.6464`
- combined total: `$0.7733`
