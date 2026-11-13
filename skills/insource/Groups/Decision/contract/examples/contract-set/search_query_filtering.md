# Search Query Filtering

- **Description:** Filtering catalog results based on user-provided queries, including
  relevance and business-rule constraints; excludes authorization checks and access-control
  filtering, and excludes client-side re-filtering of already-delivered datasets.
- **Ownership:** OoU — Backend (Layer 1).
- **Reason:** Search rules change with the business weekly; centralizing them keeps frontend
  releases out of the loop and avoids exposing catalog data the query did not earn. Database
  filtering was rejected because relevance ranking spans rules SQL cannot hold without
  migration churn. Cost paid: one round trip per query — accepted; UX latency is handled by
  pagination contracts, not by moving the owner.