# rhys contribution summary

## benchmark

This contribution covers the INTUIT physical-only single-capability subset, aligned to the public human single-capability study.

Prepared benchmark size:
- 8 physical-only templates
- 48 counterbalanced item instances
- 4 physical contexts

Contexts:
- `unexpected_contents`
- `object_drop`
- `hide_the_item`
- `ouch_that_hurt`

## human timing data

Source:
- public INTUIT results archive on OSF
- Gorilla trial-level file `human_data_single_clean.csv`

Filtering:
- remove failed attention-check participants
- remove participants with median RT below 20 seconds
- remove trials below 5 seconds from timing and accuracy summaries

Human summary on the 48-item physical subset:
- 53 included participants
- mean item-level human accuracy: `0.895`
- median item-level median RT: `26.57s`

Context-level human summary:

| context | mean human accuracy | median human seconds |
| --- | ---: | ---: |
| `hide_the_item` | 0.805 | 34.76 |
| `object_drop` | 0.983 | 23.75 |
| `ouch_that_hurt` | 0.877 | 25.28 |
| `unexpected_contents` | 0.914 | 25.89 |

The all-valid and correct-only timing axes are close. The correlation between item medians is `0.952`.

## model results

Overall accuracy:

| model | accuracy | 95% CI |
| --- | ---: | ---: |
| `gpt-5-mini` | 0.854 | [0.728, 0.928] |
| `gpt-5.4` | 0.917 | [0.804, 0.967] |
| `gpt-4.1` | 0.917 | [0.804, 0.967] |

Accuracy by human-time quartile:

| model | q1 | q2 | q3 | q4 |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5-mini` | 0.917 | 0.833 | 0.917 | 0.750 |
| `gpt-5.4` | 1.000 | 0.917 | 0.917 | 0.833 |
| `gpt-4.1` | 1.000 | 0.917 | 0.917 | 0.833 |

Context-level accuracy:

| model | hide_the_item | object_drop | ouch_that_hurt | unexpected_contents |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5-mini` | 0.833 | 1.000 | 0.583 | 1.000 |
| `gpt-5.4` | 0.917 | 1.000 | 0.750 | 1.000 |
| `gpt-4.1` | 0.917 | 1.000 | 0.750 | 1.000 |

## interpretation

The main time-horizon pattern is modest but directionally clean. Every model performs best on the fastest human-time bin and worst on the slowest bin. On this small physical subset, the largest drop is for `gpt-5-mini`, from `0.917` in the fastest bin to `0.750` in the slowest bin.

The benchmark is not monotone in raw difficulty across contexts. `hide_the_item` has the longest human times, while `ouch_that_hurt` produces the lowest model accuracy. That matters for the forward-pass framing: human time is informative here, but not sufficient by itself to explain which physical tasks stay hard.

`gpt-5.4` and `gpt-4.1` tie on overall accuracy and on every quartile bin in this subset. The gap is between those stronger models and `gpt-5-mini`, not between `gpt-5.4` and `gpt-4.1`.

## benchmark suitability note

INTUIT physical-only was a good fit for this contribution for three reasons:
- it comes with public human trial-level timing data
- it is less prominent than standard public reasoning benchmarks, which lowers obvious contamination risk
- the physical-only slice is distinct from social or theory-of-mind contributions on Rhys' sheet

The VIGNET repo includes a canary GUID and states that a private portion of the dataset is held back for future contamination checks. That is useful, but it does not prove absence from training corpora. The contamination claim here is only that this benchmark looks less exposed than more famous public reasoning sets.

## files

Main outputs:
- `results/tables/item_level_results.csv`
- `results/tables/overall_accuracy.csv`
- `results/tables/accuracy_by_time_bin.csv`
- `results/tables/accuracy_by_base_context.csv`
- `results/figures/human_time_histogram.png`
- `results/figures/accuracy_by_time_bin.png`
- `results/figures/accuracy_vs_human_time.png`
