# Scoring, gate and verdict

**Answer values:** Yes / No / Not available (default) / NA / Open. **Live values:** Pass / Fail / Not run / NA.
A test is **met** when the answer is Yes and live is not Fail. A Live-only test with no doc answer
takes its value from the live result (Pass becomes Yes, Fail becomes No).

| Metric | Formula |
|---|---|
| Capability score | sum of weights of met tests / sum of weights of non-NA tests, where P0=3, P1=2, P2=1 |
| Rating | 5 for 80 or more, 4 for 65 or more, 3 for 50 or more, 2 for 30 or more, otherwise 1 |
| Documentation completeness | share of tests not "Not available" |
| Live coverage | Live tests run (Pass or Fail) / Live tests required (those not NA) |
| Gate | each of 9 items needs all of its `all` tests met, at least one `any` test met, and (for status) a valid status map |
| Escalations | `risk` tests answered No or Open |

**Feasibility line states:**
- OK: all tests met, and live Pass where required
- BLOCKED: a P0 No, or any live Fail
- MISSING: nothing documented
- CHECK: anything else
- OK (alt): webhook or polling, where one of the two is OK

**Verdict:**
1. Gate FAIL gives **Not ready**.
2. Otherwise, any live Fail or a live test not run gives **Doc-ready, live staging verification pending**.
3. Otherwise, a score of 75 or more with 0 escalations gives **Ready (100% feasible)**.
4. Otherwise, **Ready with conditions**.
