# Distinct review of the SDK workflow correction

**PASS for correction `e8a3121da60ee448a54af42eb63953ad156f0ae6`, findings: none.**
Tree `058e9ac30f2ef4363275d8be662a46cb66f1fe8c`, parent
`ba44738ff45225c0fef757afc2b299a7591677a8`. Reviewer
`/root/sdk_dependency_probe` is distinct from `/root`, author of this correction.
This is only a review of root's workflow fix, not another review of the
reviewer's original consumer.

The preserved run39998857797 records headba447, eventpush, completed/failure,
zero jobs and zero check runs. Its page contains the actual unrecognized
`runner` expression annotation at line20/column25. This is a workflow validation
failure before consumer execution. The original RED and historical reports are
preserved; no product failure or new runtime result is inferred.

The exact three-file delta changes the workflow, appends the adoption note and
adds `workflow-correction.json`. Parsed workflow comparison confirms only two
configuration operations: remove the unavailable job-level `runner.temp`
expression and prepend the quoted environment-file write to the existing setup
step. The remaining96 base postimages are exact. Job/events, checkout pin,
working directory, toolchain, strict fmt/Clippy/build/runtime commands, four
cases, thresholds, job deadline and failure behavior are unchanged.

GitHub's primary [context availability table](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability)
excludes `runner` from `jobs.<job_id>.env`. Its
[default-variable reference](https://docs.github.com/en/actions/reference/workflows-and-actions/variables#default-environment-variables)
provides `RUNNER_TEMP` and the per-step `GITHUB_ENV` file during execution.
The correction reads those variables inside the shell; it does not try to
overwrite a reserved GitHub/runner variable.

The [environment-file contract](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#setting-an-environment-variable)
makes the new value available to subsequent steps, not automatically to the
writing step. The setup remainder only installs the toolchain and prints
`rustc -Vv`/`cargo -V`; it performs no consumer compilation or run needing the
target directory. Later Cargo steps and the quoted executable path therefore
receive the intended `$RUNNER_TEMP/host-stream-diagnostic-target` value.

A minimal equivalent probe passed using only temporary `NSEALR_CI_REVIEW_*`
variables. A shell wrote the single assignment; that writing shell still had no
new value. A separate shell, given the literal assignment as its environment,
received the exact target path, including spaces in temporary paths. Both exit
codes were0. Exact argv/output and variable mapping are in [review.json](review.json).
Temporary files were removed and no global, `GITHUB_*` or `RUNNER_*` variable was
modified. This checks shell/file propagation only; it is not hosted runner
execution or a replacement for GitHub workflow validation.

All four compiled consumer inputs remain byte-identical to a14c039 and the A02
review `06e36af3f3f2d7860e461ad5b50c8bd44f7299c1`. That distinct consumer review
remains applicable to the unchanged implementation; its historical receipt is
untouched. No rebuild, smoke replay, case change, skip, hosted CI/PR operation or
push of root's branch was performed. Root's actual PR/main hosted gates remain
pending; no Board, physical, release or parent criterion is closed here.
