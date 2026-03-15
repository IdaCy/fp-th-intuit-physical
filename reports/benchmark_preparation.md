# benchmark preparation

The prepared benchmark is the INTUIT physical-only single-capability subset aligned to the human single-capability Gorilla study.

## subset definition

Starting point:
- `battery_for_humans_single.csv`

Template inclusion rule:
- keep rows with `display == "Trial"`
- keep templates whose QA JSON has `capability_type == "single"`
- keep templates whose `metadata.required` entries all start with `physical_knowledge_`

Templates retained:
- `01.1.0.0.a`
- `01.1.0.0.b`
- `03.1.0.0.a`
- `03.1.0.0.b`
- `05.1.0.0.a`
- `05.1.0.0.b`
- `12.1.0.0.a`
- `12.1.0.0.b`

Base contexts retained:
- `unexpected_contents`
- `object_drop`
- `hide_the_item`
- `ouch_that_hurt`

Templates excluded from the single-capability battery because they require social knowledge:
- `02.*`
- `04.*`
- `06.*`
- `07.*`
- `08.*`
- `09.*`
- `10.*`
- `11.*`

## item expansion

Each retained template has six counterbalanced human instantiations in columns `C1` to `C6` with matching answer columns `A1` to `A6`.

Prepared item id format:
- `{template_id}__c{counterbalance}`

Final prepared benchmark size:
- 8 templates
- 48 item instances

## preserved fields

Each prepared row includes:
- `item_instance_id`
- `template_id`
- `counterbalance`
- `base_context`
- `physical_subcategory`
- `required_components`
- `provided_components`
- `condition`
- `inference_level`
- `vignette`
- `correct_answer_number`
- `option_1` to `option_4`

## audit

Manual checks on sampled rows confirmed:
- answer options parse correctly from the vignette text
- no duplicate `item_instance_id` values
- no missing answer options
- only the four physical contexts listed above remain
