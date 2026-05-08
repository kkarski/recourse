# How to Use Questions in Spectr

## Core Policy

- You MUST treat Spectr Q&A (`spectr qs`) as the single system of record for cross-role questions, answers, and rationale.
- You MUST NOT use `questions.md`, chat-only notes, side documents, or ad hoc messages as the primary Q&A record.
- You MUST NOT bypass Spectr CLI for role-to-role or role-to-user clarification.

## CLI Help Commands for `qs`

- You MUST run `spectr qs --help` before Q&A operations when you need command syntax confirmation.
- You MUST run `spectr qs ask --help` before creating question threads if flag usage is uncertain.
- You MUST run `spectr qs answer --help` before adding answers if flag usage is uncertain.
- You MUST run `spectr qs list --help` before filtering or including deprecated threads.
- You MUST run `spectr qs deprecate --help` before deprecating or restoring thread visibility.

## Required Question Flow

1. You MUST review existing threads before asking a new question by running `spectr qs list` (or `spectr qs list --include-deprecated` for full history).
2. You MUST ask the new question using `spectr qs ask`.
3. You MUST include role and author context (`--role` and/or `--author`) when required by team conventions.
4. You MUST capture enough context in the question body for another role to answer without ambiguity.

```bash
spectr qs list
spectr qs ask -d "What are the retry limits for failed notifications?"
```

## Required Answer Flow

1. You MUST list open threads before answering.
2. You MUST select the correct thread by `sid`.
3. You MUST answer using `spectr qs answer`.
4. You MUST include decision rationale in the answer body.
5. You MUST re-list threads when needed to verify your answer is recorded.

```bash
spectr qs list
spectr qs answer -s q-1234abcd -d "Use 3 retries with exponential backoff. Rationale: balances reliability and system load."
```

## Required Maintenance Flow

1. You MUST deprecate obsolete threads instead of deleting history.
2. You MUST use `spectr qs deprecate -s <sid>` to retire obsolete threads.
3. You MUST use `spectr qs deprecate -s <sid> --clear` to restore a thread when needed.
4. You MUST use `spectr qs list --include-deprecated` when auditing full thread history.

```bash
spectr qs deprecate -s q-1234abcd
spectr qs list --include-deprecated
```

## Behavioral Rules

- You MUST ask one clear question at a time unless a batched question is explicitly approved.
- You MUST NOT answer a question outside Spectr and then forget to record it.
- You MUST NOT proceed on silent assumptions when a blocking question remains unanswered.
- You MUST record assumptions in Spectr Q&A if work must continue before confirmation.

## Best Practices for High-Quality Q&A

- You MUST ask questions that are specific, bounded, and decision-oriented.
- You MUST include relevant context (current behavior, constraint, and impact) in each question.
- You MUST ask for the smallest missing decision that unblocks progress.
- You MUST include 3 most likely suggested answers as selectable options when asking a question to a user.
- You MUST provide an explicit option for the user to enter their own answer.
- You MUST NOT ask vague questions such as "What should we do?" without scope and criteria.

- You MUST provide answers that are explicit, actionable, and directly tied to the asked question.
- You MUST include rationale, trade-offs, and constraints in each answer when relevant.
- You MUST state assumptions clearly and mark what still needs validation.
- You MUST include acceptance implications when an answer changes requirements or behavior.
- You MUST NOT provide ambiguous answers such as "it depends" without clear decision criteria.
- You MUST NOT leave a thread without a concrete next step when the question is actionable.
