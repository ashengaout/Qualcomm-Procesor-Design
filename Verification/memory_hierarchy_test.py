"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/memory_hierarchy_test.py — pytest tests for MemoryHierarchy
"""

import pytest
from Hardware.memory_hierarchy import MemoryHierarchy, MemoryLevel, CacheLevel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_hierarchy():
    """Small hierarchy for fast tests: SSD=16, DRAM=8, L3=4, L2=2, L1=1"""
    lat = {"SSD": 3, "DRAM": 2, "L3": 1, "L2": 1, "L1": 1}
    return MemoryHierarchy(ssd_size=16, dram_size=8, l3_size=4, l2_size=2, l1_size=1, latencies=lat)


@pytest.fixture
def loaded_hierarchy():
    """Hierarchy pre-loaded with instructions in SSD."""
    lat = {"SSD": 3, "DRAM": 2, "L3": 1, "L2": 1, "L1": 1}
    mh = MemoryHierarchy(ssd_size=16, dram_size=8, l3_size=4, l2_size=2, l1_size=1, latencies=lat)
    mh.load_ssd([0x00000001, 0x00000002, 0x00000003, 0x00000004, 0x00000005])
    return mh


# ---------------------------------------------------------------------------
# Section 2 — Parameterization / size validation
# ---------------------------------------------------------------------------

class TestHierarchyValidation:

    def test_valid_sizes_accepted(self):
        #valid hierarchy should not raise
        mh = MemoryHierarchy(ssd_size=32, dram_size=16, l3_size=8, l2_size=4, l1_size=2)
        assert mh.ssd.capacity == 32
        assert mh.l1.capacity == 2

    def test_invalid_ssd_less_than_dram_raises(self):
        with pytest.raises(ValueError):
            MemoryHierarchy(ssd_size=8, dram_size=16, l3_size=4, l2_size=2, l1_size=1)

    def test_invalid_dram_less_than_l3_raises(self):
        with pytest.raises(ValueError):
            MemoryHierarchy(ssd_size=32, dram_size=4, l3_size=8, l2_size=4, l1_size=1)

    def test_invalid_equal_sizes_raises(self):
        #equal sizes also violate the strict hierarchy
        with pytest.raises(ValueError):
            MemoryHierarchy(ssd_size=16, dram_size=8, l3_size=4, l2_size=4, l1_size=1)


# ---------------------------------------------------------------------------
# Section 1 — Memory components
# ---------------------------------------------------------------------------

class TestMemoryLevel:

    def test_insert_and_contains(self):
        lvl = MemoryLevel("TEST", capacity=4, latency=1)
        lvl.insert(0xABCD)
        assert lvl.contains(0xABCD)

    def test_no_duplicate_insert(self):
        lvl = MemoryLevel("TEST", capacity=4, latency=1)
        lvl.insert(0xABCD)
        lvl.insert(0xABCD)
        assert len(lvl.storage) == 1

    def test_remove(self):
        lvl = MemoryLevel("TEST", capacity=4, latency=1)
        lvl.insert(0xABCD)
        lvl.remove(0xABCD)
        assert not lvl.contains(0xABCD)

    def test_is_full(self):
        lvl = MemoryLevel("TEST", capacity=2, latency=1)
        lvl.insert(0x0001)
        assert not lvl.is_full()
        lvl.insert(0x0002)
        assert lvl.is_full()


# ---------------------------------------------------------------------------
# Section 5 — FIFO cache eviction
# ---------------------------------------------------------------------------

class TestCacheFIFO:

    def test_fifo_evicts_oldest(self):
        #capacity 2: insert A, B, then C — A should be evicted (first-in, first-out)
        cache = CacheLevel("L1", capacity=2, latency=1)
        cache.insert(0xAAAA)
        cache.insert(0xBBBB)
        evicted = cache.insert(0xCCCC)
        assert evicted == 0xAAAA
        assert cache.contains(0xBBBB)
        assert cache.contains(0xCCCC)
        assert not cache.contains(0xAAAA)

    def test_no_eviction_when_not_full(self):
        cache = CacheLevel("L2", capacity=3, latency=1)
        evicted = cache.insert(0x1111)
        assert evicted is None

    def test_insert_existing_returns_none(self):
        cache = CacheLevel("L1", capacity=2, latency=1)
        cache.insert(0xAAAA)
        result = cache.insert(0xAAAA)
        assert result is None
        assert len(cache.storage) == 1

    def test_fifo_order_three_evictions(self):
        #fill capacity=2, then force two evictions in order
        cache = CacheLevel("L1", capacity=2, latency=1)
        cache.insert(0x0001)
        cache.insert(0x0002)
        first_evicted = cache.insert(0x0003)    # evicts 0x0001
        second_evicted = cache.insert(0x0004)   # evicts 0x0002
        assert first_evicted == 0x0001
        assert second_evicted == 0x0002


# ---------------------------------------------------------------------------
# Section 3/4 — Read operations and data movement
# ---------------------------------------------------------------------------

class TestReadOperation:

    def test_read_from_ssd_reaches_l1(self, loaded_hierarchy):
        mh = loaded_hierarchy
        found = mh.read(0x00000001)
        assert found is True
        assert mh.l1.contains(0x00000001)

    def test_read_propagates_through_all_levels(self, loaded_hierarchy):
        mh = loaded_hierarchy
        mh.read(0x00000001)
        #instruction should appear in every level on its way up
        assert mh.dram.contains(0x00000001)
        assert mh.l3.contains(0x00000001)
        assert mh.l2.contains(0x00000001)
        assert mh.l1.contains(0x00000001)

    def test_second_read_hits_l1(self, loaded_hierarchy):
        mh = loaded_hierarchy
        mh.read(0x00000001)
        initial_hits = mh.l1.hits
        mh.read(0x00000001)
        assert mh.l1.hits == initial_hits + 1

    def test_read_not_found_returns_false(self, loaded_hierarchy):
        mh = loaded_hierarchy
        result = mh.read(0xDEADBEEF)    # not in SSD
        assert result is False

    def test_read_increments_miss_counter(self, loaded_hierarchy):
        mh = loaded_hierarchy
        mh.read(0x00000001)             # cold miss
        assert mh.l1.misses == 1
        assert mh.l2.misses == 1
        assert mh.l3.misses == 1

    def test_read_l1_hit_no_miss_increment(self, loaded_hierarchy):
        mh = loaded_hierarchy
        mh.read(0x00000001)             # cold miss, fills L1
        misses_before = mh.l1.misses
        mh.read(0x00000001)             # L1 hit
        assert mh.l1.misses == misses_before  # miss count should not change


# ---------------------------------------------------------------------------
# Section 4 — Write operations
# ---------------------------------------------------------------------------

class TestWriteOperation:

    def test_write_lands_in_l1(self, small_hierarchy):
        mh = small_hierarchy
        mh.write(0xCAFEBABE)
        assert mh.l1.contains(0xCAFEBABE)

    def test_write_propagates_to_ssd(self, small_hierarchy):
        mh = small_hierarchy
        mh.write(0xCAFEBABE)
        assert mh.ssd.contains(0xCAFEBABE)

    def test_write_back_no_bypassing(self, small_hierarchy):
        mh = small_hierarchy
        mh.write(0xCAFEBABE)
        #instruction must be present at every level
        assert mh.l1.contains(0xCAFEBABE)
        assert mh.l2.contains(0xCAFEBABE)
        assert mh.l3.contains(0xCAFEBABE)
        assert mh.dram.contains(0xCAFEBABE)
        assert mh.ssd.contains(0xCAFEBABE)


# ---------------------------------------------------------------------------
# Section 3 — Clock advances during transfers
# ---------------------------------------------------------------------------

class TestClock:

    def test_clock_advances_on_read(self, loaded_hierarchy):
        mh = loaded_hierarchy
        assert mh.clock == 0
        mh.read(0x00000001)
        assert mh.clock > 0

    def test_clock_advances_on_write(self, small_hierarchy):
        mh = small_hierarchy
        mh.write(0xFFFFFFFF)
        assert mh.clock > 0

    def test_l1_hit_does_not_advance_clock(self, loaded_hierarchy):
        mh = loaded_hierarchy
        mh.read(0x00000001)             # fills L1
        clock_after_first = mh.clock
        mh.read(0x00000001)             # L1 hit — no transfer needed
        assert mh.clock == clock_after_first
