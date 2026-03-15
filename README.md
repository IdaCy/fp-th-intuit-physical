# intuit forward-pass time horizons

Reproducible benchmark contribution for Rhys' March 2026 forward-pass task completion time horizons project on the INTUIT physical-only subset.

## scope

This repo evaluates no-CoT single-call model accuracy on the INTUIT physical-only single-capability subset and compares it against public human reaction-time data from the same benchmark.

The prepared benchmark contains:
- 8 physical-only single-capability templates
- 48 counterbalanced item instances
- 4 physical contexts: `unexpected_contents`, `object_drop`, `hide_the_item`, `ouch_that_hurt`

## main results

Overall model accuracy on the 48-item physical subset:

| model | accuracy |
| --- | ---: |
| `gpt-5-mini` | 0.854 |
| `gpt-5.4` | 0.917 |
| `gpt-4.1` | 0.917 |

Human benchmark summary:
- 53 included participants after the published exclusion rules
- mean human item accuracy: 0.895
- median item-level median human time: 26.57 seconds

By human-time quartile, the slowest bin is the hardest for every model:

| model | bin 1 | bin 2 | bin 3 | bin 4 |
| --- | ---: | ---: | ---: | ---: |
| `gpt-5-mini` | 0.917 | 0.833 | 0.917 | 0.750 |
| `gpt-5.4` | 1.000 | 0.917 | 0.917 | 0.833 |
| `gpt-4.1` | 1.000 | 0.917 | 0.917 | 0.833 |

The hardest physical context is `ouch_that_hurt`. The longest human-time context is `hide_the_item`.

## setup

Create an environment and install the package:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Place API keys in `.env`:

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## reproduction

1. Download and extract the public data:

```bash
python -m src.download_data
```

2. Prepare the physical-only benchmark:

```bash
python -m src.prepare_intuit
```

3. Extract human timing statistics:

```bash
python -m src.extract_human_times
```

4. Run model evaluation:

```bash
python -m src.run_eval --model gpt-5-mini
python -m src.run_eval --model gpt-5.4
python -m src.run_eval --model gpt-4.1
```

5. Build tables and figures:

```bash
python -m src.analyze_results
python -m src.plot_results
```

## key outputs

Prepared dataset:
- `data/interim/prepared_physical_single_items.csv`

Human timing outputs:
- `data/interim/human_item_time_stats.csv`
- `results/tables/human_timing_summary.csv`

Model outputs:
- `results/model_outputs/gpt-5-mini_predictions.csv`
- `results/model_outputs/gpt-5_4_predictions.csv`
- `results/model_outputs/gpt-4_1_predictions.csv`

Merged analysis outputs:
- `results/tables/item_level_results.csv`
- `results/tables/overall_accuracy.csv`
- `results/tables/accuracy_by_time_bin.csv`
- `results/tables/accuracy_by_base_context.csv`

Figures:
- `results/figures/human_time_histogram.png`
- `results/figures/accuracy_by_time_bin.png`
- `results/figures/accuracy_vs_human_time.png`

Reports:
- `reports/data_access_notes.md`
- `reports/benchmark_preparation.md`
- `reports/methods_note.md`
- `reports/rhys_contribution_summary.md`
- `reports/rhys_message.md`
