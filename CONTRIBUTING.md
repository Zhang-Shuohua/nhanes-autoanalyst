# Contributing

Thanks for considering a contribution to NHANES AutoAnalyst.

This project values correctness over speed. Contributions are especially welcome in these areas:

1. validating variable recipes against official NHANES documentation and peer-reviewed formulas;
2. improving cycle-aware variable mappings;
3. adding tests for recipe formulas;
4. improving beginner-facing documentation;
5. adding public-health examples with clear assumptions and citations.

## Recipe contribution checklist

A new recipe should include:

- name and label;
- category: outcome, exposure, covariate, exclusion, or score;
- required raw variables and files;
- formula or derivation rule;
- inclusion/exclusion consequences;
- output variables;
- references;
- limitations;
- at least one test case or validation note.

Do not contribute restricted NHANES data or any personally identifiable data.
