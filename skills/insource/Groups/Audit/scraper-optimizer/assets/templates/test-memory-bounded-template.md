# Template: Relative Memory Boundedness Test

Use this template to add automated regression testing in CI to verify that memory consumption remains invariant to dataset size ($O(C)$ rather than $O(N)$).

---

## Python / Pytest Template (`test_memory_bounded.py`)

```python
"""
test_memory_bounded.py - Relative assertions for memory invariance and storage isolation.
"""
import os
import sys
import gc
import pytest

def get_process_rss_mb() -> float:
    """Returns current process Resident Set Size in MB."""
    import psutil
    return psutil.Process().memory_info().rss / (1024 * 1024)

class TestMemoryBoundedPipeline:
    
    @pytest.mark.asyncio
    async def test_memory_remains_invariant_under_4x_workload(self):
        """
        Invariant: Scaling workload 4x must not cause linear memory growth.
        Permitted growth ratio is < 1.30 (to account for minor runtime overheads).
        """
        gc.collect()
        base_start_rss = get_process_rss_mb()
        
        # 1. Execute baseline workload (e.g. 1,000 entities)
        from scraper_module import run_pipeline
        baseline_peak = await run_pipeline(entity_count=1_000)
        baseline_delta = max(1.0, baseline_peak - base_start_rss)
        
        gc.collect()
        stress_start_rss = get_process_rss_mb()
        
        # 2. Execute 4x stress workload (e.g. 4,000 entities)
        stress_peak = await run_pipeline(entity_count=4_000)
        stress_delta = max(1.0, stress_peak - stress_start_rss)
        
        # 3. Assert relative scaling ratio
        growth_ratio = stress_delta / baseline_delta
        assert growth_ratio < 1.30, (
            f"Memory scaled with dataset size! 4x workload produced {growth_ratio:.2f}x memory delta "
            f"(Baseline delta: {baseline_delta:.1f} MB, Stress delta: {stress_delta:.1f} MB)"
        )

    def test_checkpoint_manifest_contains_zero_payload_blobs(self, tmp_path):
        """
        Invariant: Checkpoints must store lightweight metadata manifests only.
        Raw HTML / payloads must never appear in checkpoint streams.
        """
        from scraper_module import create_checkpoint
        checkpoint_file = tmp_path / "checkpoint.jsonl"
        
        create_checkpoint(output_file=checkpoint_file, items_scraped=500)
        
        assert checkpoint_file.exists()
        total_size = checkpoint_file.stat().st_size
        
        # 500 records in manifest must remain well under 100 KB total (<200 bytes per record)
        assert total_size < 100 * 1024, f"Manifest file bloated ({total_size} bytes)! Contains payload data."
        
        # Verify forbidden raw keys
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            for line in f:
                assert '"html"' not in line, "Raw HTML payload leaked into manifest!"
                assert '"raw_body"' not in line, "Raw response body leaked into manifest!"

    def test_sparse_index_memory_ratio(self):
        """
        Invariant: In-memory sparse index overhead must be < 5% of total payload bytes.
        """
        from scraper_module.spill import ProfileSpill
        spill = ProfileSpill()
        
        payload_sample = {"data": "X" * 10_000} # 10 KB payload
        total_payload_bytes = 0
        
        for i in range(1_000): # 10 MB total payload
            spill.add(f"entity_{i}", payload_sample)
            total_payload_bytes += 10_000
            
        index_bytes = spill.get_index_memory_footprint_bytes()
        ratio = index_bytes / total_payload_bytes
        
        assert ratio < 0.05, f"Sparse index footprint exceeds 5% of payload volume: {ratio:.1%}"
```
