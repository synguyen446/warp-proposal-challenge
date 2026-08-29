# How to submit

This is a take-home. Budget about **half a day (~4 hours)** of work, and submit
within **2 days** of receiving it.

## 1. Read the brief

Read [`README.md`](README.md), then [`PROPOSAL_SPEC.md`](PROPOSAL_SPEC.md) before
writing code. The spec is the contract `validate.py` enforces, and most of the
pricing questions you are about to have are answered in it.

Meet the three must-haves first: extract facts turn by turn, price deterministically
from `data/`, output a proposal that validates. Reach for stretch goals only after
those work end to end.

## 2. Set up

- Everything you need to run `validate.py` is in the Python standard library.
- Your own pipeline can use any language and any libraries. If it is not Python,
  keep `validate.py` working by writing proposals to JSON files.
- Pricing data: read `data/` directly, or run `python mock/server.py` to get the
  same numbers over HTTP. Either is fine. There is no Warp API key for this
  exercise and none will be issued.
- Pick a free model provider (see the table in the README). Read the key from an
  environment variable. Never commit it.
- If you use a hosted model, note roughly how many calls a full run makes. Free
  tiers have daily caps and we may hit them re-running your work.

## 3. Build and check

Write one proposal JSON per call, matching
[`example/proposal.example.json`](example/proposal.example.json), which is a
complete correct proposal for the first call. Then:

```bash
python validate.py out/ --check-facts
```

This is the same validator we run on the held-out calls, so make sure it comes back
clean before you send anything. Warnings are judgment calls and do not have to be
zero, but you should be able to explain each one you left in.

## 4. Submit

1. Click **"Use this template" -> Create a new repository** at the top of this
   repo's GitHub page. Set your new repo to **Private**. Please use the template
   rather than forking, so your work stays your own.
2. Build inside your new repo. Commit as you go, we like seeing how the work
   developed.
3. When you are done, invite **`rahulharikumarr`** as a collaborator.
4. Send us:
   - the **repo link**
   - your **README**, which must include:
     - exact steps to run your tool from a clean checkout, including how to run it
       with the model disabled
     - which model provider you used and why
     - whether you read `data/` directly or went through `mock/server.py`
     - your `validate.py` output, reported honestly
     - a **"Decisions and tradeoffs"** section: what you chose, what you cut, where
       your tool fails, and what you would do next with more time
   - a **2 to 3 minute screen recording** (Loom or similar) showing a call being
     processed turn by turn, with the proposal updating as facts arrive. Include
     the moment a customer corrects themselves, and show what your tool does with
     freight it cannot price.

## 5. What happens after

We run your tool on call transcripts you have not seen, using the same validator.
Then we get on a call, walk through your code together, and ask you to extend it
live. Build something that is genuinely yours: you understand every line and can
defend every threshold.

## Ground rules

- Every figure in a proposal must be produced by your code from `data/`.
  Hand-editing outputs is disqualifying.
- Never price freight you cannot serve. Unknown lanes, hazmat, and flatbed go in
  `excluded` with a reason.
- Do not read `calls/expected/*.json` at runtime. It exists so you can check
  yourself, not so you can skip extraction.
- Using AI coding tools is encouraged. Understanding what they wrote for you is
  mandatory.
- All data here is fictional and safe to send to a free model tier. Real customer
  calls would not be, and we would expect you to treat them differently.
