# Hot-path Filtering

- **Description:** Filtering data on interaction-critical paths (client-side table re-sort,
  live filter chips) where the frontend already holds the complete authorized dataset for the
  view; excludes any filtering that would reveal records not already delivered.
- **Ownership:** OoU — Frontend (Layer 2).
- **Reason:** Round-tripping a filter the client can compute locally trades UX for nothing;
  the backend is not the bottleneck, the network is. Permitted only under the stated
  precondition — if the dataset could contain more than the user is authorized to see, this
  contract does not apply and the default rule owns the work.

## References

- Search Query Filtering — the default ownership for query filtering; this contract is its
  narrow, condition-bound exception, not a replacement.

## How To Do It

Load the authorized dataset once per view; apply filtering locally against that dataset only.
Never widen the delivery endpoint to serve this convenience — if the local set lacks the rows
the filter needs, the feature is out of scope for this contract, not permission to fetch more.