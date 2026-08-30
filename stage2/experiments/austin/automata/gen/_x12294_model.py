"""12294  x = y * (((z*y)*x)*(x*y))  --  hand model with a structurally recursive reachability predicate.

The free-model extractor needs, at the top product, the fact  EXISTS z. op(z,y) = s1  where s1 is the first
component of the encoding.  That predicate is not expressible in the closedform DSL (it would be an
unbounded chain of nested op-guards), which is why the generated 24-rule package is FALSE: 22 exhaustive
one-generator failures, all with op(z,y) itself decoded through a level-2 hole.

Here it is written directly:

    Z u A  ==  (tg A = 2 /\\ a2 A = u)                       -- A = J z u : take that z
           \\/ (u = J (J C A) (J A z) /\\ Z z C)             -- op(z,u) decoded to A

Z recurses on a2 (a2 u), a proper subterm of u, so it is a plain structural recursion with NO call to op.

The chain of the law is  s1 = op z y,  s2 = op s1 x,  s3 = op x y,  s4 = op s2 s3,  top = op y s4 = x.
Rule R1 reads the top pair as  v = J (J A x) (op x u)  with  Z u A;  it covers s1 and s3 decoding or not,
uniformly.  The remaining cases are s2 decoding and s4 decoding.
"""
import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')


def isJ(t):
    return t[0] == 'J'


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


_SZ = {}


def sz(t):
    r = _SZ.get(t)
    if r is None:
        r = 1 if t[0] == 'g' else 1 + sz(t[1]) + sz(t[2])
        _SZ[t] = r
    return r


def msr(u, v):
    m = max(sz(u), sz(v))
    return m * m + sz(u) + sz(v)


def Z(u, A):
    """exists z with op(z,u) = A -- structural recursion on u, no op call"""
    while True:
        if isJ(A) and a2(A) == u:
            return True
        if isJ(u) and isJ(a1(u)) and isJ(a2(u)) and a2(a1(u)) == A and a1(a2(u)) == A:
            u, A = a2(a2(u)), a1(a1(u))
            continue
        return False


class Model:
    def __init__(self, rules):
        self.rules = rules
        self.fired = {}
        self.memo = {}
        self.inprog = set()
        self.cycles = 0

    def opb(self, a, b, u, v):
        """op a b, but only when msr a b < msr u v (the Lean gate); None otherwise"""
        if msr(a, b) >= msr(u, v):
            return None
        return self.op(a, b)

    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None:
            return m
        if key in self.inprog:
            self.cycles += 1
            return ('J', u, v)
        self.inprog.add(key)
        res = None
        for name, f in self.rules:
            r = f(self, u, v)
            if r is not None:
                self.fired[name] = self.fired.get(name, 0) + 1
                res = r
                break
        self.inprog.discard(key)
        if res is None:
            res = ('J', u, v)
        self.memo[key] = res
        return res

    def evp(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))


# ---------------------------------------------------------------- rules

def R1(M, u, v):
    """v = J (J A x) (op x u)  with  Z u A   ->   x      (s1 / s3 free or decoded)"""
    if not (isJ(v) and isJ(a1(v))):
        return None
    x = a2(a1(v))
    if not Z(u, a1(a1(v))):
        return None
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


RULES_V1 = [('R1', R1)]


# ---- permissive variants: drop Z (an over-approximation is legal, it is only a guard) ----

def R1p(M, u, v):
    """v = J (J A x) (op x u)  ->  x"""
    if not (isJ(v) and isJ(a1(v))):
        return None
    x = a2(a1(v))
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


def R2p(M, u, v):
    """s2 decoded: v = J _ (J x u)  ->  x"""
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    return a1(a2(v))


def R2z(M, u, v):
    """s2 decoded, guarded by Z:  v = J A (J x u) with Z x A  ->  x"""
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    x = a1(a2(v))
    if not Z(x, a1(v)):
        return None
    return x


RULES_P1 = [('R1p', R1p)]
RULES_P2 = [('R1p', R1p), ('R2p', R2p)]
RULES_Z2 = [('R1', R1), ('R2z', R2z)]
RULES_M2 = [('R1', R1), ('R1p', R1p), ('R2z', R2z)]


def Z2(u, A):
    """exists z with op(z,u) = A.  Three routes, each recursing on a proper subterm of u:
         (a) A = J z u                              -- z free
         (b) u = J (J C A) (J A z)  and Z z C       -- op(z,u) fired R1 with op(A,z) free
         (c) u = J C (J A z)        and Z A C       -- op(z,u) fired R2 (s2 decoded)
    """
    if isJ(A) and a2(A) == u:
        return True
    if isJ(u) and isJ(a1(u)) and isJ(a2(u)) and a2(a1(u)) == A and a1(a2(u)) == A and Z2(a2(a2(u)), a1(a1(u))):
        return True
    if isJ(u) and isJ(a2(u)) and a1(a2(u)) == A and Z2(A, a1(u)):
        return True
    return False


def R1b(M, u, v):
    if not (isJ(v) and isJ(a1(v))):
        return None
    x = a2(a1(v))
    if not Z2(u, a1(a1(v))):
        return None
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


def R2b(M, u, v):
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    x = a1(a2(v))
    if not Z2(x, a1(v)):
        return None
    return x


RULES_B2 = [('R1b', R1b), ('R2b', R2b)]


def Zd(u, A):
    """A is a DECODED value of op(z,u) for some z (clauses b,c of Z2 only) -- used where the rule's own
    case says the product decoded, so the free route (A = J z u) must be excluded."""
    if isJ(u) and isJ(a1(u)) and isJ(a2(u)) and a2(a1(u)) == A and a1(a2(u)) == A and Z2(a2(a2(u)), a1(a1(u))):
        return True
    if isJ(u) and isJ(a2(u)) and a1(a2(u)) == A and Z2(A, a1(u)):
        return True
    return False


def R2c(M, u, v):
    """s2 decoded: v = J S2 (J x u), S2 a decoded value of op(_,x)  ->  x"""
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    x = a1(a2(v))
    if not Zd(x, a1(v)):
        return None
    return x


RULES_C2 = [('R1b', R1b), ('R2c', R2c)]


def Z3(u, A):
    """exists z with op(z,u) = A.  Over-approximation:
         (a) A = J z u
         (d) u = J (J C A) W          -- op(z,u) fired R1 (whatever W = op A z was)
         (c) u = J C (J A z), Z3 A C  -- op(z,u) fired R2
    """
    if isJ(A) and a2(A) == u:
        return True
    if isJ(u) and isJ(a1(u)) and a2(a1(u)) == A:
        return True
    if isJ(u) and isJ(a2(u)) and a1(a2(u)) == A and Z3(A, a1(u)):
        return True
    return False


def Zd3(u, A):
    if isJ(u) and isJ(a1(u)) and a2(a1(u)) == A:
        return True
    if isJ(u) and isJ(a2(u)) and a1(a2(u)) == A and Z3(A, a1(u)):
        return True
    return False


def R1d(M, u, v):
    if not (isJ(v) and isJ(a1(v))):
        return None
    x = a2(a1(v))
    if not Z3(u, a1(a1(v))):
        return None
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


def R2d(M, u, v):
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    x = a1(a2(v))
    if not Zd3(x, a1(v)):
        return None
    return x


RULES_D2 = [('R1d', R1d), ('R2d', R2d)]
RULES_D1 = [('R1d', R1d)]


def R1e(M, u, v):
    """v = J s2 (op x u) with s2 = op (a1 s2) x  and Z3 u (a1 s2)   ->  x = a2 s2"""
    if not (isJ(v) and isJ(a1(v))):
        return None
    s2 = a1(v)
    x = a2(s2)
    if not Z3(u, a1(s2)):
        return None
    if M.opb(a1(s2), x, u, v) != s2:
        return None
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


def R1f(M, u, v):
    """R1e without the Z3 guard"""
    if not (isJ(v) and isJ(a1(v))):
        return None
    s2 = a1(v)
    x = a2(s2)
    if M.opb(a1(s2), x, u, v) != s2:
        return None
    w = M.opb(x, u, u, v)
    if w is None or w != a2(v):
        return None
    return x


RULES_E2 = [('R1e', R1e), ('R2d', R2d)]
RULES_F2 = [('R1f', R1f), ('R2d', R2d)]
RULES_F1 = [('R1f', R1f)]
RULES_E1 = [('R1e', R1e)]


# ================= strict, fully structural reachability =================

def STRICT(u, v):
    """the generated R1 shape: v = J (J (J z u) x) (J x u)   (everything free)"""
    return (isJ(v) and isJ(a1(v)) and isJ(a1(a1(v))) and a2(a1(a1(v))) == u
            and isJ(a2(v)) and a2(a1(v)) == a1(a2(v)) and a2(a2(v)) == u)


def ZSdec(u, A):
    """A = op(z,u) with the product DECODED under STRICT: u = J (J (J c z) A) (J A z)"""
    return (isJ(u) and isJ(a1(u)) and isJ(a1(a1(u))) and isJ(a2(u))
            and a2(a1(u)) == A and a1(a2(u)) == A and a2(a2(u)) == a2(a1(a1(u))))


def ZS(u, A):
    return (isJ(A) and a2(A) == u) or ZSdec(u, A)


def ZSn(u, A):
    """as ZS but the free route also demands that op(a1 A, u) really is free"""
    return (isJ(A) and a2(A) == u and not STRICT(a1(A), u)) or ZSdec(u, A)


def mk_RA(Zf):
    def RA(M, u, v):
        if not (isJ(v) and isJ(a1(v))):
            return None
        x = a2(a1(v))
        if not Zf(u, a1(a1(v))):
            return None
        w = M.opb(x, u, u, v)
        if w is None or w != a2(v):
            return None
        return x
    return RA


def mk_RB(Zf):
    def RB(M, u, v):
        if not (isJ(v) and isJ(a2(v))):
            return None
        if a2(a2(v)) != u:
            return None
        x = a1(a2(v))
        if not ZSdec(x, a1(v)):
            return None
        return x
    return RB


RA_S = mk_RA(ZS); RA_SN = mk_RA(ZSn); RB_S = mk_RB(ZS)
RULES_S1 = [('RA', RA_S)]
RULES_S2 = [('RA', RA_S), ('RB', RB_S)]
RULES_SN1 = [('RA', RA_SN)]
RULES_SN2 = [('RA', RA_SN), ('RB', RB_S)]


# ================= size-gated variants of the E2 model =================

def mk_gated(rule, k):
    def R(M, u, v):
        if sz(v) <= k * sz(u):
            return None
        return rule(M, u, v)
    return R


RULES_G1 = [('R1e', mk_gated(R1e, 1)), ('R2d', mk_gated(R2d, 1))]
RULES_G2 = [('R1e', mk_gated(R1e, 2)), ('R2d', mk_gated(R2d, 2))]
RULES_G1a = [('R1e', mk_gated(R1e, 1)), ('R2d', R2d)]
RULES_H1 = [('R1d', mk_gated(R1d, 1)), ('R2d', mk_gated(R2d, 1))]


def RSTRICT(M, u, v):
    if STRICT(u, v):
        return a2(a1(v))
    return None


RULES_STRICT = [('RS', RSTRICT)]


# ================= the STRICT family: every rule recovers z from a fixed position =================
# Chain: s1 = op z y, s2 = op s1 x, s3 = op x y, s4 = op s2 s3, top = op y s4 = x.
# Rule S : nothing decoded          v = J (J (J z u) x) (J x u)
# Rule D : s1 decoded               v = J (J A     x) (J x u),  DECS u A
# Rule C : s3 decoded               v = J (J (J z u) x) s3,     op x u decoded strictly (s3 = a2 (a1 u))
# Rule CD: s1 and s3 decoded
# Rule E : s2 decoded               v = J A (J x u),            DECS x A

def DECS(u, A, d=0):
    """A = op(z,u) for some z, with the product DECODED (z is at a fixed position in u in every rule)"""
    if d > 60 or not isJ(u):
        return False
    # S route: u = J (J (J c z) A) (J A z),  z = a2 (a2 u) = a2 (a1 (a1 u))
    if (isJ(a1(u)) and isJ(a1(a1(u))) and isJ(a2(u))
            and a2(a1(u)) == A and a1(a2(u)) == A and a2(a2(u)) == a2(a1(a1(u)))):
        return True
    # D route: same shape but the inner s1 of that decode was itself decoded
    if (isJ(a1(u)) and isJ(a2(u)) and a2(a1(u)) == A and a1(a2(u)) == A
            and DECS(a2(a2(u)), a1(a1(u)), d + 1)):
        return True
    # C route: u = J (J (J c z) A) s3 with op(A,z) decoded strictly, z = a2 (a1 (a1 u))
    if isJ(a1(u)) and isJ(a1(a1(u))) and a2(a1(u)) == A:
        z = a2(a1(a1(u)))
        if STRICT(A, z) and isJ(a1(z)) and a2(a1(z)) == a2(u):
            return True
    # E route: u = J A' (J A z), z = a2 (a2 u)
    if isJ(a2(u)) and a1(a2(u)) == A and DECS(A, a1(u), d + 1):
        return True
    return False


def rS(M, u, v):
    return a2(a1(v)) if STRICT(u, v) else None


def rD(M, u, v):
    if not (isJ(v) and isJ(a1(v)) and isJ(a2(v))):
        return None
    if a2(a1(v)) != a1(a2(v)) or a2(a2(v)) != u:
        return None
    if not DECS(u, a1(a1(v))):
        return None
    return a2(a1(v))


def rC(M, u, v):
    if not (isJ(v) and isJ(a1(v)) and isJ(a1(a1(v)))):
        return None
    if a2(a1(a1(v))) != u:
        return None
    x = a2(a1(v))
    if not STRICT(x, u):
        return None
    if a2(a1(u)) != a2(v):
        return None
    return x


def rCD(M, u, v):
    if not (isJ(v) and isJ(a1(v))):
        return None
    x = a2(a1(v))
    if not DECS(u, a1(a1(v))):
        return None
    if not STRICT(x, u):
        return None
    if a2(a1(u)) != a2(v):
        return None
    return x


def rE(M, u, v):
    if not (isJ(v) and isJ(a2(v))):
        return None
    if a2(a2(v)) != u:
        return None
    x = a1(a2(v))
    if not DECS(x, a1(v)):
        return None
    return x


RULES_T = [('S', rS), ('D', rD), ('C', rC), ('CD', rCD), ('E', rE)]
RULES_T4 = [('S', rS), ('D', rD), ('C', rC), ('CD', rCD)]
RULES_T2 = [('S', rS), ('D', rD)]


RULES_U = [('S', rS), ('D', rD), ('C', rC), ('E', rE)]
RULES_U2 = [('S', rS), ('D', rD), ('C', rC)]
RULES_U3 = [('S', rS), ('C', rC), ('E', rE)]
