INTUIT physical-only single-capability contribution is done.

I aligned the benchmark to the public human single-capability Gorilla data and kept only the templates whose required metadata are physical and not social. That gives 8 templates and 48 counterbalanced item instances across `unexpected_contents`, `object_drop`, `hide_the_item`, and `ouch_that_hurt`.

Human side:
- 53 included participants after the published exclusion rules
- mean item-level human accuracy `0.895`
- median item-level median RT `26.57s`

Model side:
- `gpt-5-mini`: `0.854` overall
- `gpt-5.4`: `0.917` overall
- `gpt-4.1`: `0.917` overall

Time-bin pattern:
- every model is strongest on the fastest human-time quartile
- every model is weakest on the slowest quartile
- the biggest drop is `gpt-5-mini`, from `0.917` to `0.750`

Context pattern:
- `hide_the_item` has the longest human times
- `ouch_that_hurt` is the hardest context for the models

The repo has reproducible scripts, prepared data products, tables, figures, and a short summary in `reports/rhys_contribution_summary.md`.
