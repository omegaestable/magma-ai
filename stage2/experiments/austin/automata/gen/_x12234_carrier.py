# -*- coding: utf-8 -*-
"""Law 12234 CARRIER lab — `x = y*(((z*x)*y)*(x*y))`.

Applies the 13764 result (NOTES_13764.md): the definition block, not the rule count, is what
blows the 20,000 B cap, and only a different carrier compresses a definition block.

Chain:  A = z*x ;  B = A*y ;  C = x*y ;  D = B*C ;  goal  y*D = x.
`z` is the JUNK variable: it enters only through A, and the payload is read from C.

Carrier: M ::= g n | J a b | E a b,  tg 1/2/3, accessors total.  Every guard is a pure shape
test and every result is a subterm or a constructor application => `op` is NON-RECURSIVE.

Oracles, in the order they must be passed:
  1. exhaustive, all terms size <= 5, 2 generators              (405,224 chains)
  2. the known holes CE1..                                       (regressions)
  3. LEVEL-k DESCENT with large junk (coordinator, from gen/_w3_12087_deep3.py):
     nested encodings x_k = enc(j, x_{k-1}, y) forcing the decoder to descend k levels in the
     same argument, with z drawn from the values that trigger a decode at A.
  4. deep random
"""
import random, sys, collections

sys.setrecursionlimit(100000)
TAG = {'g': 1, 'J': 2, 'E': 3, 'G': 4}
CONS = ['J', 'E']   # constructors the term pools build with


def tg(t):  return TAG[t[0]]
def a1(t):  return t[1] if t[0] != 'g' else t
def a2(t):  return t[2] if t[0] != 'g' else t
def sz(t):  return 1 if t[0] == 'g' else sz(t[1]) + sz(t[2]) + 1


def show(t, d=0):
    if t[0] == 'g': return 'g%d' % t[1]
    if d > 6: return '<%d>' % sz(t)
    return '%s(%s,%s)' % (t[0], show(t[1], d + 1), show(t[2], d + 1))


# ---------------------------------------------------------------- candidate rule sets

def K1():
    """mark D, embed the payload: M reads x = a1 C and y = a2 C straight out of C."""
    def R(u, v):
        if tg(v) == 3 and a2(v) == u:
            return a1(v)
        return None
    def M(u, v):
        if (tg(u) == 2 and tg(v) == 2 and tg(a1(u)) != 1
                and a2(u) == a2(v) and a2(a1(u)) == a1(v)):
            return ('E', a1(v), a2(v))
        return None
    return [('R', R), ('M', M)]


REGISTRY = {'K1': K1}


def K2():
    """drop M's A-check entirely: the payload is read from C alone (`a1 v`, `a2 v`).
    Rationale: A is fed by the junk variable z and may mark/decode, so no guard may depend on it."""
    def R(u, v):
        if tg(v) == 3 and a2(v) == u:
            return a1(v)
        return None
    def M(u, v):
        if tg(u) == 2 and tg(v) == 2 and a2(u) == a2(v):
            return ('E', a1(v), a2(v))
        return None
    return [('R', R), ('M', M)]


def K3():
    """K2 plus a second reading: when v is already marked (so C mis-fired and lost the payload),
    read x out of B instead — `a2 (a1 u)` — which is the law's other path to x."""
    def R(u, v):
        if tg(v) == 3 and a2(v) == u:
            return a1(v)
        return None
    def M(u, v):
        if tg(u) == 2 and tg(v) == 2 and a2(u) == a2(v):
            return ('E', a1(v), a2(v))
        return None
    def MB(u, v):
        if tg(u) == 2 and tg(a1(u)) != 1 and tg(v) == 3:
            return ('E', a2(a1(u)), a2(u))
        return None
    return [('R', R), ('M', M), ('MB', MB)]


REGISTRY['K2'] = K2
REGISTRY['K3'] = K3


def K4():
    """M keeps BOTH arguments (`E u v`), so a mis-fired mark is still transparent: whatever
    `op x y` became, its `a2` is still `y`, so the D product still marks and the root still
    reads `a1 (a2 v)`.  R additionally demands that M's own guard held of (a1 v, a2 v)."""
    def R(u, v):
        if tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v)):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    return [('R', R), ('M', M)]


def K5():
    """K4 without R's extra conjunct."""
    def R(u, v):
        if tg(v) == 3 and a2(a2(v)) == u:
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    return [('R', R), ('M', M)]


REGISTRY['K4'] = K4
REGISTRY['K5'] = K5


def K6():
    """K4 + a last-resort mark that SYNTHESISES the C it expected out of B.
    When C decoded (so `a2 C != y` and M cannot fire at D), x and y are both still readable
    from B = J A y: x = a2 (a1 u), y = a2 u.  Emit `E u (J x y)` so the root's read is intact."""
    def R(u, v):
        if tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v)):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def MB(u, v):
        if tg(u) == 2 and tg(a1(u)) != 1:
            return ('E', u, ('J', a2(a1(u)), a2(u)))
        return None
    return [('R', R), ('M', M), ('MB', MB)]


REGISTRY['K6'] = K6


def _K4x(extra):
    """K4 with one extra conjunct on R, to stop R firing at C = op x y."""
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v)) and extra(v)):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    return [('R', R), ('M', M)]


REGISTRY['K7'] = lambda: _K4x(lambda v: tg(a1(a1(v))) != 1)
REGISTRY['K8'] = lambda: _K4x(lambda v: tg(a1(v)) == 2)
REGISTRY['K9'] = lambda: _K4x(lambda v: a2(a1(a1(v))) == a1(a2(v)))
REGISTRY['K10'] = lambda: _K4x(lambda v: tg(a2(v)) == 2)
REGISTRY['K11'] = lambda: _K4x(lambda v: tg(a1(v)) != 1 and tg(a2(v)) == 2)
REGISTRY['K12'] = lambda: _K4x(lambda v: tg(a1(v)) != 1 and tg(a2(v)) != 1)
REGISTRY['K13'] = lambda: _K4x(lambda v: tg(a2(v)) != 1)
REGISTRY['K14'] = lambda: _K4x(lambda v: tg(a1(v)) != 1)


def K15():
    """K12 + a RECOMPUTATION guard on R: `a2 v` must really be `op (a1 (a2 v)) (a2 (a2 v))`,
    i.e. the C slot must be a genuine product of the payload and u.  Structurally indistinguishable
    cases (y itself a valid encoding, so `op x y` decodes and loses the payload) are exactly what
    no shape test separates -- the same conclusion as 13764's W6.  One nested call, and the gate
    `sz (a1 (a2 v)) + sz (a2 (a2 v)) < sz u + sz v` follows from `tg (a2 v) != 1` alone."""
    box = {}
    def R(u, v):
        if not (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return None
        if box['op'](a1(a2(v)), a2(a2(v))) != a2(v):
            return None
        return a1(a2(v))
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    rules = [('R', R), ('M', M)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K15'] = K15


def K16():
    """K15 + a SECOND reading, tagged `G`, for the cell where `y` is itself a genuine encoding
    so `C = op x y` decodes and loses the payload.  x is still readable from B = J A y as
    `a2 (a1 u)`; MB certifies it by RECOMPUTING C (`op (a2 (a1 u)) (a2 u) = v`), which is what
    stops MB firing at the B position.  R2 reads the G mark without a recomputation."""
    box = {}
    def R(u, v):
        if not (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return None
        if box['op'](a1(a2(v)), a2(a2(v))) != a2(v):
            return None
        return a1(a2(v))
    def R2(u, v):
        if tg(v) == 4 and a2(a2(v)) == u:
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def MB(u, v):
        if tg(u) == 2 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('G', u, ('J', a2(a1(u)), a2(u)))
        return None
    rules = [('R', R), ('R2', R2), ('M', M), ('MB', MB)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K16'] = K16


def K17():
    """K12 (no recomputation on R) + M2, the `y`-TWICE recomputation mark.

    The open cell was: `y` is itself a genuine encoding, so `C = op x y` decodes and the payload
    leaves C, and M cannot mark D because `a2 B != a2 C`.  x is still readable from B as
    `a2 (a1 u)` and y as `a2 u`.  M2 certifies that `v` really is `op x y` -- with `a2 u` used
    TWICE, once as the recomputation's right argument and once in the emitted pair:

        M2 : tg u != 1 ∧ tg (a1 u) != 1 ∧ op (a2 (a1 u)) (a2 u) = v
             -> E u (J (a2 (a1 u)) (a2 u))

    That is what K16's fourth-constructor guard lacked: it recomputed with `v` alone, which the
    B position also satisfies.  Both recursive arguments are proper subterms of `u`, so
    sz (a2 (a1 u)) + sz (a2 u) <= sz u - 1 < sz u + sz v  holds UNCONDITIONALLY from tg u != 1 --
    an unconditional Lean gate with measure `sz u + sz v`, no msr, no fuel induction.
    """
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, ('J', a2(a1(u)), a2(u)))
        return None
    rules = [('R', R), ('M', M), ('M2', M2)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K17'] = K17


def K18():
    """K17 with design fact 2 applied to M2 as well: M2 emits `E u v` (keeping the REAL v)
    instead of synthesising `J x y`, so an M2 misfire at the B position is TRANSPARENT the way
    an M misfire is.  The payload is then recovered at the root by a second reading R2 that
    goes through B instead of C -- the law's other path to x -- certified by recomputing C
    with `a2 (a1 v)` (= y) used TWICE: once as the recomputation's right argument and once as
    the check `a2 (a1 v) = u`.

    Both recursive calls take proper subterms of ONE side, so with measure `sz u + sz v` the
    Lean gates are unconditional:
      M2 : sz (a2 (a1 u)) + sz (a2 u)             <= sz u - 1 < sz u + sz v   from tg u != 1
      R2 : sz (a2 (a1 (a1 v))) + sz (a2 (a1 v))   <= sz (a1 v) - 1 < sz v     from tg (a1 v) != 1
    """
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    rules = [('R', R), ('R2', R2), ('M', M), ('M2', M2)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K18'] = K18


def K19():
    """K18 + the `B decoded to a GENERATOR` cell.  When B is a generator, `a2 u = u`, so M's
    `a2 u = a2 v` can never hold and D is never marked.  The payload is still in C, so mark on
    the strength of `v` alone -- certified by recomputing C from its own parts (M4) -- and read
    it with R3, which drops `a2 (a1 v) = a2 (a2 v)` (meaningless when a1 v is a generator) and
    pays for it with the same recomputation.  M4 is confined to `tg u = 1` so it cannot disturb
    any cell K18 already handles."""
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def R3(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and tg(a1(v)) == 1 and tg(a2(v)) != 1
                and box['op'](a1(a2(v)), a2(a2(v))) == a2(v)):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    def M4(u, v):
        if tg(u) == 1 and tg(v) != 1 and box['op'](a1(v), a2(v)) == v:
            return ('E', u, v)
        return None
    rules = [('R', R), ('R2', R2), ('R3', R3), ('M', M), ('M2', M2), ('M4', M4)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K19'] = K19


def K20():
    """K18 + the `tg u = 1` cell, closed WITHOUT a new reading rule.

    K19's mistake was R3, not M4: a relaxed *reading* fires at `A = op z x` for any E-term x, and
    H3 forges exactly that.  So emit a mark plain `R` can already read: `E v v`.  Then
    `a2 (a1 v) = a2 C = a2 (a2 v)` holds by construction, which is precisely the conjunct that
    fails when `a1 v` is a generator -- R needs no relaxation and R3 never exists.

    The guard RECOMPUTES rather than tests shape (12087's principle): `op (a1 v) (a2 v) = v` says
    v is genuinely the product of its own parts, which H3 cannot forge because H3 forges shape,
    not evaluation.  `tg (a1 v) != 1` additionally blocks the exact A-position forge K19 died on
    (x = E g0 (J g0 g0), whose a1 is a generator).

    Gate: sz (a1 v) + sz (a2 v) = sz v - 1 < sz u + sz v, unconditional from tg v != 1.
    """
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    def M4(u, v):
        if (tg(u) == 1 and tg(v) != 1 and tg(a1(v)) != 1
                and box['op'](a1(v), a2(v)) == v):
            return ('E', v, v)
        return None
    rules = [('R', R), ('R2', R2), ('M', M), ('M2', M2), ('M4', M4)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K20'] = K20


def K21():
    """K18 + the `tg u = 1` cell, keeping design fact 2 intact.

    K20 showed the recomputation guard DOES block H3 (H3 = 0) but `E v v` discards `u`, so M4 ate
    the payload at the C position (H6 21,323).  So M4 emits `E u v` like every other mark -- its
    misfire is then transparent -- and the root gets a narrow second reading R4 for the one shape
    that creates: `a1 v` a generator.

    R4 cannot be forged at `A = op z x` because it requires `tg u != 1`, and in this cell `y` is
    provably not a generator (if it were, no rule could fire on `op _ y` at all, so B and C would
    both be free and plain M would mark D).  The recomputation `op (a1 (a2 v)) (a2 (a2 v)) = a2 v`
    is the 12087 principle: it re-runs the product rather than testing its shape.
    """
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def R4(u, v):
        if (tg(v) == 3 and tg(a1(v)) == 1 and tg(a2(v)) != 1 and tg(u) != 1
                and a2(a2(v)) == u
                and box['op'](a1(a2(v)), a2(a2(v))) == a2(v)):
            return a1(a2(v))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    def M4(u, v):
        if (tg(u) == 1 and tg(v) != 1 and tg(a1(v)) != 1
                and box['op'](a1(v), a2(v)) == v):
            return ('E', u, v)
        return None
    rules = [('R', R), ('R2', R2), ('R4', R4), ('M', M), ('M2', M2), ('M4', M4)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K21'] = K21


def K22():
    """K18 + the coordinator's named candidate: a MARK that repairs `a1 v` so plain `R` still
    applies -- no new reading, and both arguments kept, so it stays on the cheap side of the
    conservation law.  Emits `E (J u (a2 v)) v`: its `a1` has `a2 = a2 v`, which is exactly the
    conjunct `a2 (a1 v) = a2 (a2 v)` that fails when `a1 v` is a generator, and `u` is retained."""
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    def M5(u, v):
        if (tg(u) == 1 and tg(v) != 1 and tg(a1(v)) != 1
                and box['op'](a1(v), a2(v)) == v):
            return ('E', ('J', u, a2(v)), v)
        return None
    rules = [('R', R), ('R2', R2), ('M', M), ('M2', M2), ('M5', M5)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K22'] = K22


def K23():
    """The decisive experiment for the impossibility argument: a VERBATIM mark (`E u v`, cheap side
    of the conservation law) justified by `v` alone via recomputation, and NO new reading.

    If the cell were closable by a mark, this would close it: M6 marks D even when `u` is a
    generator, keeps both arguments, and its guard recomputes rather than tests shape (H3-proof).
    What it cannot do is make the ROOT read the mark -- R requires `a2 (a1 v) = a2 (a2 v)`, which
    with `a1 v = u` a generator reads `u = a2 (a2 v)`, i.e. `B = y`, false in the cell.
    """
    box = {}
    def R(u, v):
        if (tg(v) == 3 and a2(a2(v)) == u and a2(a1(v)) == a2(a2(v))
                and tg(a1(v)) != 1 and tg(a2(v)) != 1):
            return a1(a2(v))
        return None
    def R2(u, v):
        if (tg(v) == 3 and tg(a1(v)) != 1 and tg(a1(a1(v))) != 1 and a2(a1(v)) == u
                and box['op'](a2(a1(a1(v))), a2(a1(v))) == a2(v)):
            return a2(a1(a1(v)))
        return None
    def M(u, v):
        if tg(u) != 1 and tg(v) != 1 and a2(u) == a2(v):
            return ('E', u, v)
        return None
    def M2(u, v):
        if tg(u) != 1 and tg(a1(u)) != 1 and box['op'](a2(a1(u)), a2(u)) == v:
            return ('E', u, v)
        return None
    def M6(u, v):
        if (tg(u) == 1 and tg(v) != 1 and tg(a1(v)) != 1
                and box['op'](a1(v), a2(v)) == v):
            return ('E', u, v)
        return None
    rules = [('R', R), ('R2', R2), ('M', M), ('M2', M2), ('M6', M6)]
    box['op'] = mk_op(rules)[0]
    return rules


REGISTRY['K23'] = K23


def mk_op(rules):
    def opr(u, v):
        for nm, fn in rules:
            r = fn(u, v)
            if r is not None:
                return r, nm
        return ('J', u, v), 'F'
    def op(u, v):
        return opr(u, v)[0]
    return op, opr


def chain(opr, x, y, z):
    A, r1 = opr(z, x)
    B, r2 = opr(A, y)
    C, r3 = opr(x, y)
    D, r4 = opr(B, C)
    R, r5 = opr(y, D)
    return R, (r1, r2, r3, r4, r5), (A, B, C, D)


def enc(op, z, x, y):
    """the model's own encoding of x by y with junk z: op y (enc z x y) should be x."""
    return op(op(op(z, x), y), op(x, y))


# ---------------------------------------------------------------- pools

def gen_terms(maxsize, ngen):
    by = {1: [('g', i) for i in range(ngen)]}
    for n in range(2, maxsize + 1):
        out = []
        for i in range(1, n):
            j = n - 1 - i
            if j < 1: continue
            for a in by.get(i, ()):
                for b in by.get(j, ()):
                    for c in CONS:
                        out.append((c, a, b))
        by[n] = out
    return [t for n in range(1, maxsize + 1) for t in by.get(n, ())]


def rand_term(rng, depth, ngen=3):
    if depth <= 0 or rng.random() < 0.32:
        return ('g', rng.randrange(ngen))
    c = CONS[0] if rng.random() < 0.6 else CONS[rng.randrange(len(CONS))]
    return (c, rand_term(rng, depth - 1, ngen), rand_term(rng, depth - 1, ngen))


# ---------------------------------------------------------------- known holes

def CE1():
    """the single-rule baseline's hole: the root rule fires at A = op z x (sz x = 9)."""
    g0, g1, g2, g3 = [('g', i) for i in range(4)]
    return (('J', ('J', ('J', g0, g1), g2), ('J', g1, g2)), g3, g2)


HOLES = {'CE1': CE1}


# ---------------------------------------------------------------- the harness

class Run:
    def __init__(self, rules):
        self.op, self.opr = mk_op(rules)
        self.prof = collections.Counter()
        self.fails = []
        self.fired = collections.Counter()        # per-rule firing census
        self.names = [nm for nm, _ in rules]

    def one(self, x, y, z):
        try:
            R, p, mid = chain(self.opr, x, y, z)
        except RecursionError:
            return
        self.prof[p] += 1
        for t in p:
            self.fired[t] += 1
        if R != x:
            self.fails.append((x, y, z, p, mid, R))

    def report(self, n=4):
        seen = set()
        for (x, y, z, p, mid, R) in self.fails:
            if p in seen or len(seen) >= n: continue
            seen.add(p)
            print('  --- FAIL profile', ','.join(p))
            print('     x =', show(x)); print('     y =', show(y)); print('     z =', show(z))
            for nm, v in zip(('A=z*x', 'B=A*y', 'C=x*y', 'D=B*C'), mid):
                print('      %-6s = %s' % (nm, show(v)))
            print('      R      =', show(R))


def exhaustive(r, ts):
    n = 0
    for y in ts:
        for x in ts:
            for z in ts:
                r.one(x, y, z); n += 1
    return n


CENSUS = collections.Counter()


def descent(r, seed, levels, bigjunk, N):
    """LEVEL-k DESCENT (oracle 3).  x is a k-fold nested encoding; z is drawn from the values
    that make op(z,x) decode, so the same rule must fire at successive depths."""
    rng = random.Random(seed)
    small = [rand_term(rng, rng.randrange(1, 4), 2) for _ in range(120)]
    big = [rand_term(rng, rng.randrange(5, 8), 4) for _ in range(120)]   # large junk pool
    junk = big if bigjunk else small
    n = 0
    for _ in range(N):
        y = rng.choice(small)
        x = rng.choice(small)
        for _ in range(levels):                       # nest `levels` encodings of x by y
            x = enc(r.op, rng.choice(junk), x, y)
            if sz(x) > 400: break
        for z in (y, a2(x), a1(x), rng.choice(junk), a2(a2(x)), x):
            before = len(r.fails)
            r.one(x, y, z); n += 1
            try:
                _, p, _ = chain(r.opr, x, y, z)
            except RecursionError:
                continue
            CENSUS[p] += 1
            del before
    return n


def deep(r, seeds, N):
    n = 0
    for sd in seeds:
        rng = random.Random(sd)
        for _ in range(N):
            r.one(rand_term(rng, rng.randrange(6), 3), rand_term(rng, rng.randrange(6), 3),
                  rand_term(rng, rng.randrange(6), 3))
            n += 1
    return n


def validate(name, rules, verbose=True):
    print('=== %s : %d rules' % (name, len(rules)))
    r = Run(rules)
    for hn, hf in HOLES.items():
        x, y, z = hf()
        R, p, _ = chain(r.opr, x, y, z)
        print('  %s regression: profile %-16s R == x ? %s' % (hn, ','.join(p), R == x))
    ts = gen_terms(5, 2)
    n = exhaustive(r, ts); print('  exhaustive size<=5 2gen : %7d chains, %d fails' % (n, len(r.fails)))
    f0 = len(r.fails)
    for lv in (1, 2, 3):
        for bj in (False, True):
            CENSUS.clear()
            n = descent(r, 700 + lv, lv, bj, 400)
            nz = sum(c for p, c in CENSUS.items() if any(t != 'F' for t in p[:4]))
            print('  descent level=%d bigjunk=%-5s : %7d chains, %d new fails'
                  '  [census %d cells, %d with an inner decode/mark]'
                  % (lv, bj, n, len(r.fails) - f0, len(CENSUS), nz))
            f0 = len(r.fails)
    n = deep(r, (101, 202, 303), 20000)
    print('  deep 3x20,000           : %7d chains, %d new fails' % (n, len(r.fails) - f0))
    print('  TOTAL fails %d' % len(r.fails))
    print('  profiles:', ', '.join('%s=%d' % (','.join(p), c) for p, c in r.prof.most_common(10)))
    if verbose and r.fails:
        r.report()
    return r


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'K1'
    validate(which, REGISTRY[which]())


# ---------------------------------------------------------------- HARD battery (rail 50)
# Three 13764 models passed 1.7-2.3M chains and were each false to one constructed cell.
# Nothing here is a sampler over generic terms: every family forces a specific cell.

def hard(name, rules):
    print('=== HARD battery : %s' % name)
    r = Run(rules)
    op = r.op
    ts5 = gen_terms(5, 2); ts3 = gen_terms(3, 3); ts5c = gen_terms(5, 3)

    n = 0
    for y in ts5c:
        for x in ts5c:
            for z in ts3:
                r.one(x, y, z); n += 1
    print('  H1 exhaustive size<=5 3gen x z(size<=3) : %8d chains, %d fails' % (n, len(r.fails)))
    f0 = len(r.fails)

    ts7 = gen_terms(7, 2)
    n = 0
    for y in ts7:
        for x in ts5:
            for z in (('g', 0), ('g', 1), a2(y), a1(y), a2(a2(y)), a1(a1(y)), x, y):
                r.one(x, y, z); n += 1
    print('  H2 y size<=7 x size<=5 z targeted      : %8d chains, %d new fails' % (n, len(r.fails) - f0))
    f0 = len(r.fails)

    # H3: y is itself a genuine encoding of something by x  (the K12/K15 hole family)
    n = 0
    for xx in ts5:
        for w in ts5:
            for j in ts3:
                y = enc(op, j, w, xx)          # y encodes w by xx
                for z in (xx, y, w, j, a2(y), ('g', 0)):
                    r.one(xx, y, z); n += 1
    print('  H3 y a genuine encoding by x          : %8d chains, %d new fails' % (n, len(r.fails) - f0))
    f0 = len(r.fails)

    # H4: z is an encoding, so A = op z x decodes; and z = y
    n = 0
    for xx in ts5:
        for yy in ts5:
            for j in ts3:
                for z in (enc(op, j, xx, yy), enc(op, j, yy, xx), yy, enc(op, j, j, xx)):
                    r.one(xx, yy, z); n += 1
    print('  H4 z an encoding / z = y              : %8d chains, %d new fails' % (n, len(r.fails) - f0))
    f0 = len(r.fails)

    # H5: chain-value coincidence -- x,y,z drawn from the model's own products
    rng = random.Random(4242); n = 0
    pool = ts3 + [rand_term(rng, 3, 3) for _ in range(60)]
    for _ in range(40000):
        x0 = rng.choice(pool); y0 = rng.choice(pool); z0 = rng.choice(pool)
        A = op(z0, x0); B = op(A, y0); C = op(x0, y0); D = op(B, C)
        c = [x0, y0, z0, A, B, C, D, op(y0, D), ('J', x0, y0), ('E', x0, y0), a2(D), a1(D)]
        r.one(rng.choice(c), rng.choice(c), rng.choice(c)); n += 1
    print('  H5 chain-value coincidence            : %8d chains, %d new fails' % (n, len(r.fails) - f0))
    f0 = len(r.fails)

    # H6: deep random, 8 seeds, depth <= 6, 4 generators
    n = 0
    for sd in (11, 22, 33, 44, 55, 66, 77, 88):
        rng = random.Random(sd)
        for _ in range(25000):
            r.one(rand_term(rng, rng.randrange(7), 4), rand_term(rng, rng.randrange(7), 4),
                  rand_term(rng, rng.randrange(7), 4)); n += 1
    print('  H6 deep 8x25,000 depth<=6 4gen        : %8d chains, %d new fails' % (n, len(r.fails) - f0))
    f0 = len(r.fails)

    # H7: level-k descent, k up to 5, both junk pools, more instances
    for lv in (1, 2, 3, 4, 5):
        for bj in (False, True):
            CENSUS.clear()
            n = descent(r, 9000 + lv, lv, bj, 900)
            nz = sum(c for p, c in CENSUS.items() if any(t != 'F' for t in p[:4]))
            print('  H7 descent k=%d bigjunk=%-5s        : %8d chains, %d new fails'
                  '  [census %d cells, %d inner]' % (lv, bj, n, len(r.fails) - f0, len(CENSUS), nz))
            f0 = len(r.fails)

    tot = sum(r.prof.values())
    print('  TOTAL %d chains, %d fails, %d distinct profiles' % (tot, len(r.fails), len(r.prof)))
    print('  FIRING CENSUS: ' + ', '.join('%s=%d' % (n, r.fired.get(n, 0)) for n in r.names + ['F']))
    never = [n for n in r.names if r.fired.get(n, 0) == 0]
    print('  RULES NEVER FIRED: %s' % (never if never else 'none -- every rule is exercised'))
    if r.fails:
        r.report(4)
    else:
        print('  CLEAN')
    return r
