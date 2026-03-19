# estimating the time horizons for intuit physical-only reasoning

Rhys, March 2026

This contribution estimates forward-pass task completion time horizons on the INTUIT physical-only single-capability subset using public human trial-level timing data from the corresponding Gorilla study. The core result is that `gpt-5.4` already reaches `0.917` accuracy in the strict no-CoT setting and rises to `0.958` with either a light CoT condition or a repeated-problem prompt. The slowest human-time quartile remains the hardest under every tested condition.

INTUIT physical-only is useful here for three reasons. It comes with public human timing data, it is less exposed than standard headline reasoning benchmarks, and the physical-only slice is distinct from social or theory-of-mind tasks that other contributors are more likely to cover. The benchmark is also a clean fit for single-call evaluation because each item is a short self-contained vignette with a four-way answer set.

## results

Overall accuracy on the 48-item subset:

| model | condition | accuracy |
| --- | --- | ---: |
| `gpt-5-mini` | `no_cot` | 0.854 |
| `gpt-5.4` | `no_cot` | 0.917 |
| `gpt-5.4` | `cot` | 0.958 |
| `gpt-5.4` | `repeat` | 0.958 |
| `gpt-4.1` | `no_cot` | 0.917 |

Accuracy by human-time quartile:

| model | condition | q1 | q2 | q3 | q4 |
| --- | --- | ---: | ---: | ---: | ---: |
| `gpt-5-mini` | `no_cot` | 0.917 | 0.833 | 0.917 | 0.750 |
| `gpt-5.4` | `no_cot` | 1.000 | 0.917 | 0.917 | 0.833 |
| `gpt-5.4` | `cot` | 1.000 | 1.000 | 0.917 | 0.917 |
| `gpt-5.4` | `repeat` | 1.000 | 1.000 | 0.917 | 0.917 |
| `gpt-4.1` | `no_cot` | 1.000 | 0.917 | 0.917 | 0.833 |

The main pattern is stable. The fastest human-time bin is easiest and the slowest bin is hardest in every tested condition. The stronger `gpt-5.4` prompting variants improve the second quartile and the slowest quartile by one item each relative to the strict no-CoT baseline.

At the context level, `hide_the_item` is the longest-time human context while `ouch_that_hurt` remains the weakest model context. CoT and repeated-problem prompting raise `gpt-5.4` to perfect accuracy on `hide_the_item`, but `ouch_that_hurt` still tops out at `0.833`.

## implementation details

The benchmark starts from the public INTUIT single-capability human battery. I kept only templates whose required metadata components are physical and not social. That leaves 8 templates:

- `01.1.0.0.a`
- `01.1.0.0.b`
- `03.1.0.0.a`
- `03.1.0.0.b`
- `05.1.0.0.a`
- `05.1.0.0.b`
- `12.1.0.0.a`
- `12.1.0.0.b`

Each template has six counterbalanced human instantiations, giving 48 item instances across four contexts:

- `unexpected_contents`
- `object_drop`
- `hide_the_item`
- `ouch_that_hurt`

## human time estimates

Human timing comes from `paper_results/human_data_single_clean.csv` in the public OSF results archive. Filtering follows the published INTUIT notebook:

- keep Gorilla rows with `Display == "Trial"` and `Screen == "vignette"`
- remove participants who fail the attention check
- remove participants with median reaction times below 20 seconds
- remove trials below 5 seconds from timing and accuracy summaries

This leaves 53 included participants on the final 48-item physical subset. Mean item-level human accuracy is `0.895`. The median item-level median reaction time is `26.57s`.

The quartile bins used for the main plots have median human times of about:

- q1: `21.01s`
- q2: `25.13s`
- q3: `28.76s`
- q4: `36.88s`

## prompting conditions

All evaluations use a single API call per item.

`no_cot`
- strict one-digit answer only

`cot`
- the model may reason briefly
- the response must end with `Final answer: <digit>`

`repeat`
- the vignette is shown twice
- the model still answers with one digit only

The final `gpt-5.4` CoT and repeat runs completed with zero parse failures.

## interpretation

This benchmark gives a modest but clean forward-pass time-horizon signal. Human time tracks single-call model difficulty, but not perfectly. The longest-time tasks are not identical to the lowest-accuracy tasks, which means time horizon is informative but not sufficient by itself to explain where physical reasoning stays hard.

The added CoT and repeated-problem conditions help, but only slightly. On this subset they each buy two additional correct answers for `gpt-5.4`, moving from `0.917` to `0.958`. That suggests the original no-CoT result was already close to the benchmark ceiling, but there is still some room for extra performance once the prompt allows more explicit or more careful processing.

## caveats and future work

- The benchmark is small at 48 items.
- Human time is an empirical task-difficulty proxy, not a direct measure of model latent computation.
- The repeated-problem condition is exploratory.
- This is one physical reasoning slice, not a global estimate of forward-pass horizons.

The next obvious extensions would be:

- run the same CoT condition on `gpt-5-mini`
- add a filler-token condition if we want to match Ryan-style experiments more closely
- pool this contribution with the other benchmark tabs to fit a broader scaling picture
