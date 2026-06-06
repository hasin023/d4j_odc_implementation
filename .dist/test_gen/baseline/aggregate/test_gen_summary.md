# Test Generation Analysis Report

## Aggregate Metrics

- **Total bugs**: 2
- **Compiled**: 2 (100%)
- **Fails on buggy** (of compiled): 2 (100%)
- **Passes on fixed** (of compiled): 0
- **Oracle match** (fails buggy AND passes fixed): 0 (0%)
- **Method name match rate**: 0%
- **Modified class targeted rate**: 100%
- **Refinement used**: 0 (0%)
- **Fault detection kept through refinement**: 0 (0% of refined)
- **Oracle match achieved through refinement**: 0 (0% of refined)
- **Avg refine iterations** (when used): 0.0

## Per Prompt Style (Ablation)

| Style | Total | Compiled | Fault Detection | Oracle Match |
|-------|-------|----------|-----------------|--------------|
| full | 2 | 2 (100%) | 2 (100%) | 0 (0%) |

## Per Project Breakdown

| Project | Total | Compiled | Fault Detection | Oracle Match |
|---------|-------|----------|-----------------|--------------|
| Time | 2 | 2 (100%) | 2 (100%) | 0 (0%) |

## Per-Bug Details

| Bug | Style | Compiled | Fails Buggy | Passes Fixed | Oracle | Notes |
|-----|-------|----------|-------------|--------------|--------|-------|
| Time-25 | full | Y | Y | N | N |  |
| Time-27 | full | Y | Y | N | N |  |
