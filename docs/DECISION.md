# How the decision works

## Answers
Each check gets one answer: Yes / No / Not available (the default) / NA / Open.
Checks marked Sandbox also get a sandbox result: Pass / Fail / Not run.

| A check is | When |
|---|---|
| Met | the answer is Yes (or NA) and it did not fail on sandbox |
| Open | the answer is Open: partly documented, and the vendor needs to confirm |
| Missing | Not available, No, or failed on sandbox |

## Must-haves (the only things that decide)
There are 7 groups. A group is Met when all its checks are Met (and, where it says "any one of",
at least one of those is Met). It is Missing if any required check is Missing, or if any check in the group failed on sandbox (even an "any one of" alternative).

1. Place an order and get an order ID back (ORD-01, ORD-02)
2. Our address fields fit their order format (ORD-05)
3. Product ID from their catalogue is what the order takes (CAT-03)
4. Get the order status (STS-01, STS-03, and any one of WHK-01 / POL-01)
5. Get courier and tracking number (TRK-01)
6. Retry safely without duplicate orders (IDM-01, and any one of IDM-02 / IDM-03)
7. Secure login that works (AUTH-01, SEC-01)

## Decision
| Can we integrate? | When |
|---|---|
| No, we cannot integrate yet | any must-have is Missing |
| Likely yes, after the vendor answers a few points | none Missing, some Open |
| Yes on paper, confirm with a sandbox test | all Met in the docs, sandbox not run |
| Yes, we can integrate | all Met and passed on sandbox |

## Does the API work?
| Result | When |
|---|---|
| Not tested yet | no sandbox run |
| Partly tested | some sandbox checks passed, none failed |
| Works on sandbox | every sandbox check passed |
| Problems found | at least one sandbox check failed (listed) |

## Everything else
Important and Nice-to-have checks are counted ("Important 15 of 89 covered") and listed as gaps
with questions for the vendor. They never change the decision. The 4 `risk` checks (signed
webhooks, non-JSON webhooks, unsupported encryption, an order failing before confirmation) add
the note "needs a change on our side first".
