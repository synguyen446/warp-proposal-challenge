# Warp - Live Proposal Builder Challenge

A Warp sales rep is on a video call with an enterprise prospect. The prospect is
describing their freight out loud, in the messy way people actually talk: a volume
here, a correction there, a requirement mentioned in passing forty seconds later.

By the time that call ends, the rep wants a priced, accurate, defensible proposal
on screen. Not a follow-up email two days later. On screen, during the call,
updating as the customer talks.

That is what you are building a lite version of.

Budget about **half a day (~4 hours)** and submit within **2 days**. We care far
more about the decisions you make than about how many features you finish. A
smaller thing done well beats a broad thing half-working.

## What you build

A tool that consumes a call transcript **turn by turn** and maintains a live
proposal. Three parts:

1. **Extract.** Pull structured deal facts out of conversational speech: lanes,
   pallet counts, monthly volumes, weights, service levels, accessorial needs.
   Customers correct themselves, speak in ranges, and use words like "skid" and
   "kilo". Your extraction has to cope.

2. **Price.** Compute the proposal deterministically from the CSVs in `data/`.
   Rate lookup, mode selection, fuel, accessorials, volume tier, totals.
   **The language model never does arithmetic.** See
   [`PROPOSAL_SPEC.md`](PROPOSAL_SPEC.md) for the exact formulas.

3. **Present.** Produce the proposal object in
   [`proposal.schema.json`](proposal.schema.json), including the prose a rep can
   actually read aloud, and an honest account of what you could not price.
   [`example/proposal.example.json`](example/proposal.example.json) is a complete,
   correct proposal for `call_01_northwind`. Read it first; it is the fastest way
   to understand the output format.

### The part that makes this hard

It has to be **incremental**. Feed the transcript in one turn at a time and the
proposal must update as facts arrive. When the customer says "actually make that
seven pallets, not six" at minute three, the proposal revises. It does not append
a second lane, and it does not need the call to end first.

A command line tool that prints the current proposal state after each turn is a
perfectly good way to show this. A web UI is a stretch goal, not a requirement.

This is the difference between a proposal builder and a transcript summarizer, and
it is most of what we are looking at.

## What you are given

```
data/rate_card.csv       50 lanes with LTL and FTL pricing and transit days
data/accessorials.csv    liftgate, inside delivery, sort and segregate, detention...
data/volume_tiers.csv    monthly shipment count -> discount
data/service_levels.csv  standard, expedited, guaranteed
data/pricing_config.csv  fuel surcharge, FTL thresholds, detention free hours
data/account_history.csv eight existing Warp accounts, for comparables

calls/call_0*.txt        six recorded sales calls
calls/expected/*.json    the deal facts each call actually contains

example/                 one complete, correct proposal to model your output on

mock/server.py           the same pricing data over HTTP, if you want it
```

All of it is fictional. There is no real Warp pricing in this repo.

**You never need a Warp API key.** None exists for this exercise. Read the CSVs
directly, or run [`mock/server.py`](mock/README.md), which serves the same numbers
over HTTP with no dependencies and no key. Both paths are equally acceptable and
produce identical pricing.

The mock is there for anyone who wants to build the more realistic version. On a
real call the rate engine is a service, so it can be slow or briefly down while a
customer is talking:

```bash
python mock/server.py --latency --flaky
```

What your tool shows the rep in that moment is a genuine design question, and one
of the more interesting things you can put in your writeup.

The six calls are not six copies of the same call. Between them they include a
customer who corrects their own numbers mid-sentence, a lane Warp has no rate for,
freight Warp cannot legally or physically move, a customer buying the wrong mode
out of habit, metric units, and a competitor's number being used as leverage. Each
one is asking whether your tool does something sensible or something confident and
wrong.

## Checking your work

Before writing any code, watch the validator pass on the worked example:

```bash
python validate.py example/proposal.example.json
```

Then, once your pipeline is producing proposals:

```bash
python validate.py out/                 # every proposal you produced
python validate.py out/ --check-facts   # also score extraction against calls/expected/
```

Pure standard library, nothing to install. It checks two separate things:

- **Pricing consistency.** Given the facts your proposal states, does your math
  follow the spec? Every line item is recomputed from the rate card. This is the
  hard gate, and it is where hallucinated numbers die.
- **Extraction accuracy** (`--check-facts`). Do the facts you pulled from the
  transcript match what the customer actually said?

Warnings are judgment calls, not failures. Read them.

**The held-out calls.** We have more transcripts, written the same way, that you
never see. After you submit we run your tool on those. That is the run that counts,
so tuning to these six is wasted effort.

## About the AI

We want to see you use a model. We are not going to ask an intern to pay for
tokens, so use a free tier. Options that cost nothing:

| Option | What it takes | Rough free limits |
|---|---|---|
| [Groq](https://console.groq.com) | Email, no card | ~30 requests/min, generous daily cap |
| [Google AI Studio](https://aistudio.google.com) | Google account | Gemini Flash, roughly 1,000+ requests/day |
| [GitHub Models](https://github.com/marketplace/models) | The GitHub account you already have | ~10 requests/min, tens to low hundreds/day |
| [Ollama](https://ollama.com) | A local install, works offline | Unlimited, bounded by your laptop |

These limits move around, so check the provider rather than trusting this table.
Free tiers also generally train on what you send them. Everything here is
fictional, so that does not matter for this exercise. It would matter enormously
with a real customer call, and we would expect you to know the difference.

Two requirements around this:

1. **Provider-agnostic.** Put the model call behind one small interface. We may
   run your code with a different provider than you did, and we should not have to
   rewrite your pipeline to do it.
2. **It must degrade.** Your tool has to run with the model turned off, via a
   `--no-ai` flag or equivalent, falling back to whatever rules you can write.
   Pricing must be identical either way, because pricing was never the model's job.
   Sales calls happen when APIs are down, and a rep on a call cannot wait.

If you cannot get any key working, build the rules-based path and say so. You will
be judged on the pipeline and the reasoning, not on which vendor you got a token
from.

## Rules

- **Every number in your proposal must come from your code**, computed from
  `data/`. Hand-editing figures into the JSON is disqualifying, and it shows up
  immediately on the held-out run.
- **Do not price what you cannot serve.** If a lane is not in the rate card, or
  the freight is hazmat or needs a flatbed, it goes in `excluded` with a reason.
  Inventing a number there is the worst failure available in this exercise,
  because in the real world someone signs it.
- Your tool must run from a clean checkout using the steps in your README.
- Keep API keys out of the repo. Read them from the environment.
- `calls/expected/*.json` is for checking yourself. Reading it at runtime instead
  of extracting from the transcript defeats the entire exercise and will be
  obvious on the held-out calls.

## Stretch goals

Only after the three must-haves work end to end.

- **Show the delta.** When a fact changes mid-call, show what moved in the
  proposal and by how much. Reps get asked "what did that just do to the price".
- **The comparable.** Pull the closest account from `account_history.csv` and give
  the rep a sentence they can use as a proof point.
- **A UI.** Anything the rep could actually have open during the call.
- **Confidence.** Mark facts the model is unsure about so the rep knows what to
  confirm out loud before it becomes a contract.

## Using AI to build this

Encouraged. Use Claude Code, Cursor, Copilot, whatever you are fastest in. We
expect fluency with these tools. The one thing that matters is that the result is
yours: you understand every line, the design calls were deliberate, and you can
explain and extend it live on a follow-up call. AI-generated code you cannot
defend is what sinks a submission, not the AI.

## How to submit

See [`SUBMISSION.md`](SUBMISSION.md). In short: click **"Use this template"** to
make your own private repo, build, invite `rahulharikumarr`, and send us the link,
your README, and a short screen recording.

## What we value

Judgment over coverage. Whether your tool knows what it does not know. Whether the
prices reconcile. Whether a real rep could hold this on a real call without getting
embarrassed. A submission that prices three lanes correctly and refuses the fourth
with a clear reason beats one that prices all four with one of them invented.
