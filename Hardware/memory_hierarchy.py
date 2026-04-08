"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/memory_hierarchy.py — Memory Hierarchy Simulation (SSD -> DRAM -> L3 -> L2 -> L1)
"""

from collections import deque

# PendingTransfer — tracks an in-flight data move between two levels

class PendingTransfer:
    def __init__(self, instruction, from_level, to_level, cycles_remaining, final_dest=None):
        self.instruction = instruction          # 32-bit integer
        self.from_level = from_level            # source level name (str)
        self.to_level = to_level                # destination level name (str)
        self.cycles_remaining = cycles_remaining
        self.final_dest = final_dest or to_level  # ultimate destination for chained transfers


# MemoryLevel — base storage tier used for SSD and DRAM

class MemoryLevel:
    def __init__(self, name, capacity, latency):
        self.name = name
        self.capacity = capacity                # max number of 32-bit instructions
        self.latency = latency                  # cycles to complete a transfer from this level
        self.storage = []                       # list of 32-bit int instructions

    def contains(self, instruction):
        return instruction in self.storage

    def insert(self, instruction):
        if instruction not in self.storage:
            if self.is_full():
                self.storage.pop(0)     # evict oldest (FIFO) to stay within capacity
            self.storage.append(instruction)

    def remove(self, instruction):
        if instruction in self.storage:
            self.storage.remove(instruction)

    def is_full(self):
        return len(self.storage) >= self.capacity


# CacheLevel — extends MemoryLevel with FIFO eviction and hit/miss tracking

class CacheLevel(MemoryLevel):
    def __init__(self, name, capacity, latency):
        super().__init__(name, capacity, latency)
        self.fifo_queue = deque()               # left = oldest, right = newest
        self.hits = 0
        self.misses = 0

    #insert instruction; evict oldest (FIFO) if full — returns evicted instruction or None
    def insert(self, instruction):
        if instruction in self.storage:
            return None
        evicted = None
        if self.is_full():
            evicted = self.fifo_queue.popleft()     # oldest out
            self.storage.remove(evicted)
        self.storage.append(instruction)
        self.fifo_queue.append(instruction)         # newest to right
        return evicted

    def remove(self, instruction):
        if instruction in self.storage:
            self.storage.remove(instruction)
            self.fifo_queue = deque(x for x in self.fifo_queue if x != instruction)


# MemoryHierarchy — orchestrates all levels, clock, and transfers

class MemoryHierarchy:

    #default transfer latencies in clock cycles
    DEFAULT_LATENCIES = {
        "SSD":  100,
        "DRAM":  20,
        "L3":     5,
        "L2":     2,
        "L1":     1,
    }

    def __init__(self, ssd_size=1024, dram_size=256, l3_size=64, l2_size=16, l1_size=4, latencies=None):
        #enforce hierarchy size constraint: SSD > DRAM > L3 > L2 > L1
        if not (ssd_size > dram_size > l3_size > l2_size > l1_size):
            raise ValueError(
                f"Hierarchy size constraint violated: "
                f"SSD({ssd_size}) > DRAM({dram_size}) > L3({l3_size}) "
                f"> L2({l2_size}) > L1({l1_size}) must hold."
            )

        lat = latencies if latencies else self.DEFAULT_LATENCIES

        self.ssd  = MemoryLevel("SSD",  ssd_size,  lat["SSD"])
        self.dram = MemoryLevel("DRAM", dram_size, lat["DRAM"])
        self.l3   = CacheLevel("L3",   l3_size,   lat["L3"])
        self.l2   = CacheLevel("L2",   l2_size,   lat["L2"])
        self.l1   = CacheLevel("L1",   l1_size,   lat["L1"])

        #ordered from slowest/largest to fastest/smallest
        self.levels = [self.ssd, self.dram, self.l3, self.l2, self.l1]
        self._level_map = {lvl.name: lvl for lvl in self.levels}

        self.clock = 0
        self.pending_transfers = []
        self.access_log = []

    # Clock management
    def tick(self):
        #advance clock one cycle and resolve any completed transfers
        self.clock += 1
        completed = [xfer for xfer in self.pending_transfers if xfer.cycles_remaining <= 1]
        for xfer in self.pending_transfers:
            xfer.cycles_remaining -= 1

        for xfer in completed:
            self.pending_transfers.remove(xfer)
            dest = self._level_map[xfer.to_level]

            #insert into destination; cache levels may evict an old entry
            evicted = None
            if isinstance(dest, CacheLevel):
                evicted = dest.insert(xfer.instruction)
            else:
                dest.insert(xfer.instruction)

            msg = (f"  [Cycle {self.clock}] Transfer complete: "
                   f"{xfer.instruction:#010x}  {xfer.from_level} -> {xfer.to_level}")
            self.access_log.append(msg)
            print(msg)

            #if part of a chained transfer and not yet at final destination, schedule next hop
            if xfer.to_level != xfer.final_dest:
                names = [lvl.name for lvl in self.levels]
                cur_idx = names.index(xfer.to_level)
                fin_idx = names.index(xfer.final_dest)
                if fin_idx > cur_idx:
                    next_level = self.levels[cur_idx + 1]
                else:
                    next_level = self.levels[cur_idx - 1]
                self._schedule_transfer(xfer.instruction, xfer.to_level, next_level.name, xfer.final_dest)

            #if a FIFO eviction happened, write evicted block down one level
            if evicted is not None:
                lower = self._lower_level(xfer.to_level)
                if lower:
                    evict_msg = (f"  [Cycle {self.clock}] FIFO eviction: "
                                 f"{evicted:#010x} evicted from {dest.name} -> {lower.name}")
                    self.access_log.append(evict_msg)
                    print(evict_msg)
                    self._schedule_transfer(evicted, dest.name, lower.name)

    def _advance_until_idle(self):
        #tick until no transfers are in flight
        while self.pending_transfers:
            self.tick()

    # Internal helpers
    def _schedule_transfer(self, instruction, from_name, to_name, final_dest=None):
        src = self._level_map[from_name]
        xfer = PendingTransfer(
            instruction=instruction,
            from_level=from_name,
            to_level=to_name,
            cycles_remaining=src.latency,
            final_dest=final_dest or to_name,
        )
        self.pending_transfers.append(xfer)

    def _lower_level(self, level_name):
        #return the level one step closer to SSD, or None if already SSD
        names = [lvl.name for lvl in self.levels]
        idx = names.index(level_name)
        return self.levels[idx - 1] if idx > 0 else None

    def _upper_level(self, level_name):
        #return the level one step closer to CPU, or None if already L1
        names = [lvl.name for lvl in self.levels]
        idx = names.index(level_name)
        return self.levels[idx + 1] if idx < len(self.levels) - 1 else None

    def _promote_to_l1(self, instruction, found_at):
        #schedule only the first hop; tick() chains each subsequent hop until L1
        next_level = self._upper_level(found_at)
        if next_level:
            self._schedule_transfer(instruction, found_at, next_level.name, final_dest="L1")

    # Public operations
    def load_ssd(self, instructions: list):
        #pre-populate SSD with a list of 32-bit instructions
        for instr in instructions[:self.ssd.capacity]:
            self.ssd.insert(instr)
        msg = f"[Init] SSD loaded with {len(self.ssd.storage)} instructions."
        self.access_log.append(msg)
        print(msg)

    def read(self, instruction: int) -> bool:
        """
        Fetch an instruction through the hierarchy into L1.
        Checks L1 first, then L2, L3, DRAM, SSD (no bypassing).
        Returns True if found, False otherwise.
        """
        log_prefix = f"[Cycle {self.clock}] READ {instruction:#010x}"

        #check cache levels L1 -> L2 -> L3 for a hit
        for cache in [self.l1, self.l2, self.l3]:
            if cache.contains(instruction):
                cache.hits += 1
                msg = f"{log_prefix} -- HIT at {cache.name}"
                self.access_log.append(msg)
                print(msg)
                #promote to L1 if hit was at L2 or L3
                if cache.name != "L1":
                    self._promote_to_l1(instruction, cache.name)
                    self._advance_until_idle()
                return True

        #all caches missed — search DRAM then SSD
        found_at = None
        if self.dram.contains(instruction):
            found_at = "DRAM"
        elif self.ssd.contains(instruction):
            found_at = "SSD"

        if found_at is None:
            msg = f"{log_prefix} -- NOT FOUND in hierarchy"
            self.access_log.append(msg)
            print(msg)
            for cache in [self.l1, self.l2, self.l3]:
                cache.misses += 1
            return False

        #record miss on all cache levels
        for cache in [self.l1, self.l2, self.l3]:
            cache.misses += 1

        msg = f"{log_prefix} -- MISS (all caches) -- found at {found_at}, promoting..."
        self.access_log.append(msg)
        print(msg)

        self._promote_to_l1(instruction, found_at)
        self._advance_until_idle()
        return True

    def write(self, instruction: int):
        """
        Write an instruction into L1 only (write-back policy).
        Data propagates to lower levels only when evicted by FIFO replacement.
        """
        msg = f"[Cycle {self.clock}] WRITE {instruction:#010x} -- written to L1"
        self.access_log.append(msg)
        print(msg)

        #write into L1 immediately; FIFO eviction cascades down via tick()
        evicted = self.l1.insert(instruction)
        if evicted is not None:
            evict_msg = f"  FIFO eviction from L1: {evicted:#010x} -> L2"
            self.access_log.append(evict_msg)
            print(evict_msg)
            self._schedule_transfer(evicted, "L1", "L2", final_dest="SSD")

        self._advance_until_idle()

    # Output / reporting
    def print_config(self):
        print("\n" + "=" * 60)
        print("  Memory Hierarchy Configuration")
        print("=" * 60)
        print(f"  {'Level':<14} {'Capacity':>10}  {'Latency':>10}")
        print(f"  {'-'*14} {'-'*10}  {'-'*10}")
        for lvl in self.levels:
            label = f"{lvl.name} (cache)" if isinstance(lvl, CacheLevel) else lvl.name
            print(f"  {label:<14} {lvl.capacity:>7} instrs  {lvl.latency:>5} cycles")
        print(f"\n  Hierarchy: SSD > DRAM > L3 > L2 > L1 (enforced)")
        print(f"  Replacement policy : FIFO (cache levels L1/L2/L3)")
        print(f"  Instruction width  : 32-bit")
        print("=" * 60)

    def print_trace(self):
        print("\n" + "=" * 60)
        print("  Instruction Access Trace")
        print("=" * 60)
        for entry in self.access_log:
            print(f"  {entry}")

    def print_stats(self):
        print("\n" + "=" * 60)
        print("  Cache Hit / Miss Statistics")
        print("=" * 60)
        print(f"  {'Level':<6} {'Hits':>8} {'Misses':>8} {'Hit Rate':>10}")
        print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*10}")
        for cache in [self.l1, self.l2, self.l3]:
            total = cache.hits + cache.misses
            rate = f"{cache.hits / total * 100:.1f}%" if total > 0 else "N/A"
            print(f"  {cache.name:<6} {cache.hits:>8} {cache.misses:>8} {rate:>10}")

    def print_final_state(self):
        print("\n" + "=" * 60)
        print("  Final State of Each Memory Level")
        print("=" * 60)
        for lvl in self.levels:
            used = len(lvl.storage)
            print(f"\n  {lvl.name} ({used}/{lvl.capacity} instructions used):")
            if lvl.storage:
                for instr in lvl.storage:
                    print(f"    {instr:#010x}")
            else:
                print("    (empty)")
        print(f"\n  Total clock cycles elapsed: {self.clock}")
        print("=" * 60)
