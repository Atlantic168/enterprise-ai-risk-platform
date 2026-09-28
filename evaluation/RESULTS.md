# Evaluation Results

## Summary

| Metric | Result |
|---|---:|
| Retrieval Hit@3 | 15/15 (100.00%) |
| Average `/ask` latency | 2.611 s |
| Median `/ask` latency | 2.465 s |
| P95 `/ask` latency | 3.583 s |
| SQL accuracy | 10/10 (100.00%) |
| Unsupported-question abstention | 5/5 (100.00%) |

## Evaluation Setup

### Retrieval Quality

15 curated questions were created with known expected source documents. A query was counted as a hit when the expected source appeared in the top three retrieved results.

### End-to-End Latency

10 requests were sent through the Dockerized `/ask` endpoint. Latency includes the application request, RAG retrieval, and HKUST GenAI API inference.

### SQL Accuracy

10 validation cases compared the controlled SQL tool output with independently executed PostgreSQL queries using the same parameters.

### Unsupported-Question Handling

5 questions were created for information that was not present in the policy knowledge base. Responses were manually reviewed to determine whether the system correctly abstained instead of generating unsupported factual claims.

## Interpretation

These results are prototype-level validation results based on small, curated evaluation datasets. They should not be interpreted as production-scale benchmarks.

## Limitations

The current evaluation does not measure performance on large or continuously changing enterprise datasets. Further work should use larger, more diverse, and automated regression test sets.