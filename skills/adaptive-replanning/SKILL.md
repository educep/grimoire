---
name: adaptive-replanning
description: How an unattended build loop should react when a step fails. Instead of restarting the whole plan or retrying the same step, it replans the remaining work from the current state so each failure teaches the next attempt. Use when explaining, tuning, or debugging why the loop replanned or stopped.
---

# Adaptive replanning

This is what turns a batch runner into a loop. A plain runner fixes its plan once, up front, and when a step fails it either gives up on the rest or retries the same step until it happens to pass. Adaptive replanning treats a failure as new information and works out the remaining plan from where things actually are, not from where they started.

## The idea

Picture the planner as a search toward one goal: every slice of work landed. A naive run commits to a single path at the start, so when a step on that path fails the path is already wrong, and repeating it changes nothing. Replan from the current state instead:

- The starting point is the current state, not the original one. Anything already done is finished and left alone, and the replanner never reissues it.
- The failure is a route you now know is blocked. Feed its cause (the review findings, the open question, the error) into the replan so the next path is genuinely different, not the same move again.
- The output is a fresh plan for the work that remains: reorder it, split a task, insert a missing prerequisite, rewrite the approach, or give up on a goal that unattended work honestly cannot reach.

Failures accumulate as lessons carried forward, not as a retry loop over the first plan.

## Two loops, kept separate

Two loops sit one inside the other, and it helps to keep them distinct.

The fix loop is the inner one. It works on a single task: when a review comes back failing, the same task runs again with the findings in hand. It stops after a fixed number of attempts.

The replan loop is the outer one. It works on the whole remaining plan: when a slice still won't land after the fix loop is spent, or a worker is blocked, or a task errors out, the loop rederives what to do next from the current state. It stops after a replan budget you set.

The fix loop retries the same work. Only the replan loop changes the plan. A slice counts as landed only once every track has finished all of its tasks.

## The cycle

1. Run a slice. If it lands, move to the next one.
2. If it fails to land and the replan budget is spent, stop, and mark the untried tasks as skipped so nothing is silently dropped.
3. Otherwise replan from the current state, given the goal, the finished work (left untouched), the failure and its cause, the queue that remains, and the lessons so far.
4. The replanner either returns a revised set of remaining tasks, which replace the queue, or decides to stop and says why.

Revised tasks use the same shape as the original ones, so they run through the same build and review machinery. A replan is not a special case for anything downstream.

## What resuming and replanning must respect

- **Resume residue.** Re-running a worker that died holding partial edits re-applies its work on
  top of its own residue. Revert the residue first, or treat the orphaned diff as an unreviewed
  draft and verify it before anything builds on it.
- **Killed is not failed.** An externally interrupted step — including a measurement — is
  relaunched as-is, not replanned around and not converted into a question for the human. Replan on
  *causes*, not on interruptions.
- **Stale scope is replanned, never resumed.** When the world has moved under an unstarted part of
  the plan (entries closed by other work, premises disproven), resuming implements stale scope.
  Re-plan that part from current reality — and keep the stale text verbatim as the replan's input,
  because the drift between old and new is itself the evidence that re-deriving pays.
- **Refusal is an outcome, not a failure.** A worker that disproves its task's premise by execution
  has finished — a plan instruction is a hypothesis like any other, and an executor may retract it
  by derivation. The replan records the disproof, corrects the sources that carried the wrong
  premise, and does not reissue the task.

## Reading the result

A run should report enough to audit the path it took: how many times it replanned, the lessons the failures taught, whether and why it stopped early, and which tasks were skipped because it stopped first. Emit a start and a done marker for every step, plus each step's token cost, so a step that hangs is obvious rather than invisible.

## Tuning the replan budget

The replan budget is the backstop for an unattended run. A higher budget gives more chances to route around a hard failure at the cost of more time and tokens, and setting it to zero turns replanning off, so the first failed slice stops the run. Set it to the number of genuinely different approaches worth trying before a person should step in.

If the loop keeps stopping on the same cause, that is the signal that a design question is still open. Take it back to the design stage, settle it, and rerun. Adaptive replanning routes around dead ends in execution. It does not invent product decisions; by design it stops on those and hands them back.
