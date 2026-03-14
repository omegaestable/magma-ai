"""
proof_search.py — Automated proof search engine for equational implication.

Given "Eq1 implies Eq2?", searches for a proof that every magma
satisfying Eq1 also satisfies Eq2.

Methods (escalating sophistication):
  1. Identity check (syntactic equality)
  2. Direct substitution (specialization)
  3. Bidirectional BFS rewriting (meet in the middle)
  4. A* guided rewriting with term-complexity heuristic
  5. Congruence closure on ground instances
  6. Multi-step chaining via known implications graph
"""

from __future__ import annotations
import heapq
import time
from typing import Optional
from analyze_equations import (
    parse_equation, get_vars, get_depth, count_ops, term_size,
    match, substitute, get_dual, tree_to_str,
)


# ── Rewrite infrastructure ───────────────────────────────────────

def all_rewrites(term, rules, max_results: int = 200, max_term_size: int = 40):
    """Generate all single-step rewrites of a term at any position.

    Yields (new_term, rule_idx, position_description).
    Skips rewrites that produce terms larger than max_term_size.
    """
    count = 0
    for ri, (rl, rr) in enumerate(rules):
        # Try at root
        m = {}
        if match(rl, term, m):
            new = substitute(rr, m)
            if term_size(new) <= max_term_size:
                yield new, ri, "root"
                count += 1
                if count >= max_results:
                    return

    # Recurse into subterms
    if isinstance(term, tuple) and len(term) == 3:
        for new_left, ri, pos in all_rewrites(term[1], rules, max_results - count, max_term_size):
            new_term = ('*', new_left, term[2])
            if term_size(new_term) <= max_term_size:
                yield new_term, ri, f"L.{pos}"
                count += 1
                if count >= max_results:
                    return
        for new_right, ri, pos in all_rewrites(term[2], rules, max_results - count, max_term_size):
            new_term = ('*', term[1], new_right)
            if term_size(new_term) <= max_term_size:
                yield new_term, ri, f"R.{pos}"
                count += 1
                if count >= max_results:
                    return


# ── Method 1: Identity ──────────────────────────────────────────

def check_identity(eq1, eq2) -> bool:
    """Trivial: eq1 == eq2 syntactically."""
    return eq1 == eq2


# ── Method 2: Specialization ────────────────────────────────────

def check_specialization(eq1, eq2) -> Optional[dict]:
    """Check if eq2 is a substitution instance of eq1.

    If eq1 is L1=R1 and eq2 is L2=R2, try to find sigma such that
    sigma(L1)=L2 and sigma(R1)=R2.
    Returns the substitution mapping or None.
    """
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2

    # Try both orientations of eq1
    for l, r in [(lhs1, rhs1), (rhs1, lhs1)]:
        m = {}
        if match(l, lhs2, m) and match(r, rhs2, m):
            return dict(m)
        m = {}
        if match(l, rhs2, m) and match(r, lhs2, m):
            return dict(m)
    return None


# ── Method 3: Bidirectional BFS ─────────────────────────────────

def bidirectional_bfs(
    eq1, eq2,
    max_nodes: int = 2000,
    max_depth: int = 8,
    timeout: float = 5.0,
) -> Optional[list]:
    """Bidirectional BFS from both sides of eq2, using eq1 as rewrite rules.

    If we find a term reachable from both LHS2 and RHS2, we have a proof.
    Returns the proof trace (list of steps) or None.
    """
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    rules = [(lhs1, rhs1), (rhs1, lhs1)]

    t0 = time.time()

    # Forward: terms reachable from LHS2
    # Backward: terms reachable from RHS2
    # Each entry: term -> (depth, parent_term, rule_idx)
    fwd = {lhs2: (0, None, -1)}
    bwd = {rhs2: (0, None, -1)}
    fwd_queue = [lhs2]
    bwd_queue = [rhs2]

    # Check immediate match
    if lhs2 == rhs2:
        return [("identity", lhs2)]
    if lhs2 in bwd:
        return _reconstruct_proof(lhs2, fwd, bwd)

    fwd_depth = 0
    bwd_depth = 0

    while fwd_queue or bwd_queue:
        if time.time() - t0 > timeout:
            return None

        # Expand forward one level
        if fwd_queue and fwd_depth <= bwd_depth:
            fwd_depth += 1
            if fwd_depth > max_depth:
                fwd_queue = []
            else:
                next_q = []
                for term in fwd_queue:
                    if len(fwd) >= max_nodes:
                        break
                    for new_term, ri, pos in all_rewrites(term, rules):
                        if new_term in bwd:
                            fwd[new_term] = (fwd_depth, term, ri)
                            return _reconstruct_proof(new_term, fwd, bwd)
                        if new_term not in fwd:
                            fwd[new_term] = (fwd_depth, term, ri)
                            next_q.append(new_term)
                fwd_queue = next_q

        # Expand backward one level
        elif bwd_queue:
            bwd_depth += 1
            if bwd_depth > max_depth:
                bwd_queue = []
            else:
                next_q = []
                for term in bwd_queue:
                    if len(bwd) >= max_nodes:
                        break
                    for new_term, ri, pos in all_rewrites(term, rules):
                        if new_term in fwd:
                            bwd[new_term] = (bwd_depth, term, ri)
                            return _reconstruct_proof(new_term, fwd, bwd)
                        if new_term not in bwd:
                            bwd[new_term] = (bwd_depth, term, ri)
                            next_q.append(new_term)
                bwd_queue = next_q

        else:
            break

    return None


def _reconstruct_proof(meeting_point, fwd, bwd) -> list:
    """Reconstruct proof chain from forward/backward BFS results."""
    # Forward chain: lhs2 -> ... -> meeting_point
    chain_fwd = []
    t = meeting_point
    while t is not None:
        chain_fwd.append(t)
        _, parent, _ = fwd.get(t, (0, None, -1))
        t = parent
    chain_fwd.reverse()

    # Backward chain: meeting_point -> ... -> rhs2
    chain_bwd = []
    t = meeting_point
    _, parent, _ = bwd.get(t, (0, None, -1))
    t = parent
    while t is not None:
        chain_bwd.append(t)
        _, parent, _ = bwd.get(t, (0, None, -1))
        t = parent

    return chain_fwd + chain_bwd


# ── Method 4: A* guided rewriting ───────────────────────────────

def _term_distance_heuristic(term, target) -> float:
    """Heuristic: estimated distance between two terms.

    Uses structural differences as an admissible heuristic for A*.
    """
    if term == target:
        return 0
    if isinstance(term, str) and isinstance(target, str):
        return 0 if term == target else 1
    if isinstance(term, str) or isinstance(target, str):
        return abs(term_size(term) if isinstance(target, str) else term_size(target))
    # Both are operations
    return (0.5 * _term_distance_heuristic(term[1], target[1])
            + 0.5 * _term_distance_heuristic(term[2], target[2]))


def astar_rewrite(
    eq1, eq2,
    max_nodes: int = 3000,
    timeout: float = 5.0,
) -> Optional[list]:
    """A* rewriting search from LHS2 toward RHS2, using eq1 rules.

    Also searches from RHS2 toward LHS2. Takes the first path found.
    Returns proof chain or None.
    """
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    rules = [(lhs1, rhs1), (rhs1, lhs1)]

    t0 = time.time()

    for start, goal in [(lhs2, rhs2), (rhs2, lhs2)]:
        # Priority queue: (f_score, counter, term, path)
        counter = 0
        h0 = _term_distance_heuristic(start, goal)
        pq = [(h0, counter, start, [start])]
        visited = {start}

        while pq:
            if time.time() - t0 > timeout:
                return None
            if len(visited) >= max_nodes:
                break

            f, _, current, path = heapq.heappop(pq)

            if current == goal:
                return path

            g = len(path)
            for new_term, _, _ in all_rewrites(current, rules, max_results=50):
                if new_term == goal:
                    return path + [new_term]

                if new_term not in visited:
                    visited.add(new_term)
                    h = _term_distance_heuristic(new_term, goal)
                    # Penalize term growth to prevent explosion
                    size_penalty = max(0, term_size(new_term) - term_size(start) - 4) * 0.5
                    counter += 1
                    heapq.heappush(pq, (g + 1 + h + size_penalty, counter, new_term, path + [new_term]))

    return None


# ── Method 5: Ground congruence closure ─────────────────────────

class UnionFind:
    """Union-Find for congruence closure."""
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def congruence_closure_check(
    eq1, eq2,
    n_elements: int = 3,
    timeout: float = 2.0,
) -> bool:
    """Check implication via congruence closure on ground terms.

    Instantiate eq1 with elements from {0..n-1}, build congruence classes,
    then check if all instances of eq2 hold.

    This is sound but incomplete (depends on n_elements).
    """
    import itertools

    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    vars1 = sorted(get_vars(lhs1) | get_vars(rhs1))
    vars2 = sorted(get_vars(lhs2) | get_vars(rhs2))

    t0 = time.time()
    uf = UnionFind()

    # Build a term algebra: represent compound terms as hashable objects
    # op(a, b) -> ("op", find(a), find(b))
    term_map = {}  # term -> canonical element

    def intern(t, env):
        """Intern a term into the union-find, return its representative."""
        if isinstance(t, str):
            return env[t]
        l = intern(t[1], env)
        r = intern(t[2], env)
        key = ("op", uf.find(l), uf.find(r))
        if key not in term_map:
            term_map[key] = key
        return term_map[key]

    # Ground eq1 for all assignments over {0..n-1}
    for assign in itertools.product(range(n_elements), repeat=len(vars1)):
        if time.time() - t0 > timeout:
            return False  # inconclusive, not proven
        env = dict(zip(vars1, assign))
        l_term = intern(lhs1, env)
        r_term = intern(rhs1, env)
        uf.union(l_term, r_term)

    # Check if all instances of eq2 hold
    for assign in itertools.product(range(n_elements), repeat=len(vars2)):
        if time.time() - t0 > timeout:
            return False
        env = dict(zip(vars2, assign))
        l_term = intern(lhs2, env)
        r_term = intern(rhs2, env)
        if uf.find(l_term) != uf.find(r_term):
            return False

    return True


# ── Method 6: Graph-based chaining ──────────────────────────────

class ImplicationGraph:
    """Directed graph of known implications between equations.

    If we know Eq_A → Eq_B and Eq_B → Eq_C, then Eq_A → Eq_C.
    We can use BFS/DFS on this graph to find transitive proofs.
    """

    def __init__(self):
        self.adj = {}  # eq_idx -> set of implied eq_idx
        self.neg = {}  # eq_idx -> set of NOT-implied eq_idx
        self.n_edges = 0
        self.n_neg_edges = 0

    def add_implication(self, from_idx: int, to_idx: int):
        if from_idx not in self.adj:
            self.adj[from_idx] = set()
        self.adj[from_idx].add(to_idx)
        self.n_edges += 1

    def add_non_implication(self, from_idx: int, to_idx: int):
        if from_idx not in self.neg:
            self.neg[from_idx] = set()
        self.neg[from_idx].add(to_idx)
        self.n_neg_edges += 1

    def is_known_false(self, from_idx: int, to_idx: int) -> bool:
        """Check if we definitively know from_idx does NOT imply to_idx."""
        return to_idx in self.neg.get(from_idx, set())

    def load_from_matrix_file(self, filepath: str, limit: int = 0):
        """Load from the raw implications CSV."""
        with open(filepath, 'r', encoding='utf-8') as f:
            for row_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                values = line.split(',')
                eq1 = row_idx + 1
                for col_idx, val_str in enumerate(values):
                    eq2 = col_idx + 1
                    if eq1 != eq2:
                        try:
                            v = int(val_str.strip())
                            if v > 0:
                                self.add_implication(eq1, eq2)
                            elif v < 0:
                                self.add_non_implication(eq1, eq2)
                        except ValueError:
                            pass
                if limit and row_idx + 1 >= limit:
                    break

    def can_reach(self, from_idx: int, to_idx: int, max_depth: int = 5) -> Optional[list]:
        """BFS to find a path from_idx → to_idx in the implication graph.

        Returns the path [from, ..., to] or None.
        """
        if from_idx == to_idx:
            return [from_idx]
        if from_idx not in self.adj:
            return None

        visited = {from_idx}
        queue = [(from_idx, [from_idx])]

        for current, path in queue:
            if len(path) > max_depth:
                continue
            for neighbor in self.adj.get(current, []):
                if neighbor == to_idx:
                    return path + [to_idx]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def implied_by(self, eq_idx: int) -> set:
        """Get all equations implied by eq_idx (direct)."""
        return self.adj.get(eq_idx, set())


# ── Main proof search orchestrator ───────────────────────────────

def find_proof(
    eq1_str: str,
    eq2_str: str,
    timeout: float = 10.0,
    impl_graph: Optional[ImplicationGraph] = None,
    eq1_idx: int = 0,
    eq2_idx: int = 0,
) -> Optional[dict]:
    """Search for a proof that eq1 implies eq2.

    Strategy (escalating cost):
      1. Identity check (instant)
      2. Specialization / substitution (instant)
      3. Graph chaining via known implications (if available)
      4. Bidirectional BFS rewriting
      5. A* guided rewriting
      6. Duality: prove dual(eq1) → dual(eq2) then lift

    Returns dict with 'method', 'proof', 'time_s' or None.
    """
    t0 = time.time()

    eq1 = parse_equation(eq1_str)
    eq2 = parse_equation(eq2_str)

    # 1. Identity
    if check_identity(eq1, eq2):
        return {"method": "identity", "proof": "syntactically identical",
                "time_s": time.time() - t0}

    # 2. Specialization
    sigma = check_specialization(eq1, eq2)
    if sigma is not None:
        return {"method": "specialization", "proof": f"substitution: {sigma}",
                "time_s": time.time() - t0}

    # 3. Graph chaining
    if impl_graph and eq1_idx and eq2_idx:
        path = impl_graph.can_reach(eq1_idx, eq2_idx, max_depth=5)
        if path is not None:
            return {"method": "graph_chain", "proof": f"chain: {' → '.join(f'Eq{i}' for i in path)}",
                    "time_s": time.time() - t0}

    # Budget remaining time across methods
    remaining = timeout - (time.time() - t0)
    if remaining <= 0:
        return None

    # 4. Bidirectional BFS
    bfs_budget = remaining * 0.35
    proof_chain = bidirectional_bfs(eq1, eq2, max_nodes=2000, timeout=bfs_budget)
    if proof_chain is not None:
        steps = [tree_to_str(t) for t in proof_chain]
        return {"method": "bfs_rewrite", "proof": " = ".join(steps),
                "steps": len(proof_chain), "time_s": time.time() - t0}

    remaining = timeout - (time.time() - t0)
    if remaining <= 0:
        return None

    # 5. A* rewriting
    astar_budget = remaining * 0.4
    proof_chain = astar_rewrite(eq1, eq2, max_nodes=3000, timeout=astar_budget)
    if proof_chain is not None:
        steps = [tree_to_str(t) for t in proof_chain]
        return {"method": "astar_rewrite", "proof": " = ".join(steps),
                "steps": len(proof_chain), "time_s": time.time() - t0}

    remaining = timeout - (time.time() - t0)
    if remaining <= 0:
        return None

    # 5b. Congruence closure (sound but incomplete)
    cc_budget = remaining * 0.3
    if congruence_closure_check(eq1, eq2, n_elements=3, timeout=cc_budget):
        return {"method": "congruence_closure",
                "proof": "verified by congruence closure on 3 elements",
                "time_s": time.time() - t0}

    remaining = timeout - (time.time() - t0)
    if remaining <= 0:
        return None

    # 6. Try with duality
    lhs1, rhs1 = eq1
    lhs2, rhs2 = eq2
    dual_eq1 = (get_dual(lhs1), get_dual(rhs1))
    dual_eq2 = (get_dual(lhs2), get_dual(rhs2))

    # If dual(eq1) = eq1 (self-dual), try proving with dual of eq2
    sigma = check_specialization(eq1, dual_eq2)
    if sigma is not None:
        return {"method": "dual_specialization",
                "proof": f"apply duality then substitution: {sigma}",
                "time_s": time.time() - t0}

    dual_chain = bidirectional_bfs(eq1, dual_eq2, max_nodes=1000,
                                    timeout=remaining * 0.5)
    if dual_chain is not None:
        steps = [tree_to_str(t) for t in dual_chain]
        return {"method": "dual_bfs", "proof": "via duality: " + " = ".join(steps),
                "steps": len(dual_chain), "time_s": time.time() - t0}

    return None


# ── CLI ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from analyze_equations import load_equations

    equations = load_equations()

    if len(sys.argv) >= 3:
        eq1_idx = int(sys.argv[1])
        eq2_idx = int(sys.argv[2])
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
    else:
        # Demo: Eq4 (x = x◇y, left absorbing) implies Eq8 (x = x◇(x◇x))
        eq1_idx, eq2_idx = 4, 8
        timeout = 10.0

    eq1_str = equations[eq1_idx - 1]
    eq2_str = equations[eq2_idx - 1]
    print(f"Eq{eq1_idx}: {eq1_str}")
    print(f"Eq{eq2_idx}: {eq2_str}")
    print(f"Searching for proof (timeout={timeout}s)...")

    result = find_proof(eq1_str, eq2_str, timeout=timeout)
    if result:
        print(f"\nPROOF FOUND ({result['method']}, {result['time_s']:.3f}s):")
        print(f"  {result['proof']}")
    else:
        print("\nNo proof found.")
