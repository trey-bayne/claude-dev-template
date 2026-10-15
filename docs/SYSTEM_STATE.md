# System State — as of [date]

## What's running
[list of services, versions, current config]

## Established patterns
[the coding patterns that emerged during the build and are now the standard — the ones a
new contributor would otherwise get wrong. Write them as pipelines or rules, one line each.]

<!-- Shape to follow, from a real project's file:
     - All new endpoints: auth middleware → owner filter → handler
     - All new records: owner field required, enforced by the store
     - All new intake pipelines: blob store → queue → index + graph + registry
     Replace these with THIS project's patterns. They are examples of the form,
     not defaults to inherit. -->

## Known constraints discovered during build
[things that weren't in the original CLAUDE.md but matter]

## What was explicitly not built and why
[deferred features, rejected approaches, scope decisions made during build]
