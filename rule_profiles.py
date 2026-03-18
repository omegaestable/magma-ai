import re
from dataclasses import dataclass
from dataclasses import field


def normalize(eq: str) -> str:
    return eq.replace(' ', '')


def parse_sides(eq: str) -> tuple[str, str]:
    return tuple(eq.split('=', 1))


def count_ops(term: str) -> int:
    return term.count('*')


def get_vars(term: str) -> set[str]:
    return set(re.findall(r'[a-z]', term))


def is_bare_var(term: str) -> bool:
    return len(term) == 1 and term.isalpha()


def leftmost_var(term: str) -> str | None:
    for char in term:
        if char.isalpha():
            return char
    return None


def rightmost_var(term: str) -> str | None:
    for char in reversed(term):
        if char.isalpha():
            return char
    return None


def canonicalize(eq: str) -> str:
    mapping: dict[str, str] = {}
    next_vars = iter('xyzwuvabcdefghijklmnopqrst')
    out: list[str] = []
    for char in eq:
        if char.isalpha():
            if char not in mapping:
                mapping[char] = next(next_vars)
            out.append(mapping[char])
        else:
            out.append(char)
    return ''.join(out)


def same_law(e1: str, e2: str) -> bool:
    return canonicalize(e1) == canonicalize(e2)


def is_singleton_forcing(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    if is_bare_var(lhs) and lhs not in get_vars(rhs):
        return True
    if is_bare_var(rhs) and rhs not in get_vars(lhs):
        return True
    return False


def left_proj_satisfies(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    return leftmost_var(lhs) == leftmost_var(rhs)


def right_proj_satisfies(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    return rightmost_var(lhs) == rightmost_var(rhs)


def const_satisfies(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    lhs_has_op = count_ops(lhs) > 0
    rhs_has_op = count_ops(rhs) > 0
    if lhs_has_op and rhs_has_op:
        return True
    if not lhs_has_op and not rhs_has_op:
        return lhs == rhs
    return False


def parity_satisfies(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    for var in get_vars(lhs) | get_vars(rhs):
        if (len(re.findall(var, lhs)) % 2) != (len(re.findall(var, rhs)) % 2):
            return False
    return True


def is_balanced(eq: str) -> bool:
    lhs, rhs = parse_sides(eq)
    return count_ops(lhs) == count_ops(rhs)


@dataclass(frozen=True)
class CheatsheetProfile:
    name: str
    left_family: set[str]
    right_family: set[str]
    const_family: set[str]
    square_right_sources: set[str]
    square_right_targets: set[str]
    square_left_sources: set[str]
    square_left_targets: set[str]
    c887_sources: set[str] = field(default_factory=set)
    c887_targets: set[str] = field(default_factory=set)
    left_generic_enabled: bool = True
    left_generic_require_x_absent: bool = False
    right_generic_enabled: bool = True
    right_generic_require_x_absent: bool = False


GRAPH_V4 = CheatsheetProfile(
    name='graph_v4',
    left_family={
        canonicalize('x=x*y'),
        canonicalize('x=x*(y*z)'),
        canonicalize('x=x*(y*(x*z))'),
        canonicalize('x=x*(y*(z*y))'),
        canonicalize('x=x*((y*z)*w)'),
    },
    right_family={
        canonicalize('x=y*x'),
        canonicalize('x=(y*z)*x'),
        canonicalize('x=((y*y)*z)*x'),
        canonicalize('x=(y*(y*(y*z)))*x'),
        canonicalize('x=((y*z)*w)*x'),
    },
    const_family={
        canonicalize('x*y=z*w'),
        canonicalize('x*y=y*z'),
        canonicalize('x*y=z*y'),
        canonicalize('x*x=y*z'),
        canonicalize('x*y=(y*x)*z'),
        canonicalize('x*y=(y*z)*x'),
    },
    square_right_sources={
        canonicalize('x=y*(x*x)'),
        canonicalize('x=(y*x)*(y*x)'),
        canonicalize('x=(y*(y*z))*(w*x)'),
        canonicalize('x=(y*(y*x))*(z*x)'),
    },
    square_right_targets={
        canonicalize('x=((x*y)*x)*(z*x)'),
        canonicalize('x=y*(z*(w*(u*x)))'),
        canonicalize('x*y=z*(y*(w*y))'),
    },
    square_left_sources={
        canonicalize('x=(x*x)*y'),
        canonicalize('x=(x*y)*(z*z)'),
    },
    square_left_targets={
        canonicalize('x*x=x*((y*z)*w)'),
    },
)


GRAPH_V7 = CheatsheetProfile(
    name='graph_v7',
    left_family={
        canonicalize('x=x*y'),
        canonicalize('x=x*(y*z)'),
        canonicalize('x=x*((y*z)*w)'),
        canonicalize('x=x*(y*(z*y))'),
        canonicalize('x=x*(y*((z*w)*u))'),
        canonicalize('x=x*((y*z)*(w*u))'),
        canonicalize('x=x*((y*(z*w))*w)'),
        canonicalize('x=x*(((y*z)*w)*u)'),
        canonicalize('x=x*((y*z)*(z*z))'),
        canonicalize('x=x*(y*(x*z))'),
        canonicalize('x=x*(y*(z*(x*y)))'),
        canonicalize('x=x*(y*(x*(z*w)))'),
    },
    right_family={
        canonicalize('x=y*x'),
        canonicalize('x=(y*z)*x'),
        canonicalize('x=((y*z)*z)*x'),
        canonicalize('x=((y*y)*z)*x'),
        canonicalize('x=((y*z)*w)*x'),
        canonicalize('x=(y*(y*(y*z)))*x'),
        canonicalize('x=(((y*x)*y)*z)*x'),
        canonicalize('x=(y*(y*z))*x'),
        canonicalize('x=(((y*z)*x)*z)*x'),
        canonicalize('x=(((y*y)*z)*w)*x'),
        canonicalize('x=((y*(z*y))*w)*x'),
        canonicalize('x=(y*((z*x)*w))*x'),
        canonicalize('x=(((y*z)*y)*w)*x'),
        canonicalize('x=(((y*x)*z)*y)*x'),
        canonicalize('x=(y*((x*z)*z))*x'),
    },
    const_family={
        canonicalize('x*y=z*w'),
        canonicalize('x*y=y*z'),
        canonicalize('x*y=z*y'),
        canonicalize('x*x=y*z'),
        canonicalize('x*y=(y*x)*z'),
        canonicalize('x*y=(y*z)*x'),
        canonicalize('x*y=y*((x*y)*z)'),
        canonicalize('x*y=((z*w)*x)*u'),
        canonicalize('x*y=((z*y)*x)*x'),
        canonicalize('x*y=(y*y)*(z*w)'),
        canonicalize('x*y=z*(w*(z*u))'),
        canonicalize('x*y=z*(x*(w*x))'),
        canonicalize('x*y=z*(w*(u*u))'),
        canonicalize('x*y=(z*w)*(w*z)'),
        canonicalize('x*y=y*(z*(y*z))'),
        canonicalize('x*y=(z*z)*(w*x)'),
        canonicalize('x*y=(z*w)*(z*x)'),
        canonicalize('x*y=(y*y)*z'),
        canonicalize('x*y=((z*y)*y)*w'),
        canonicalize('x*y=y*((z*w)*w)'),
        canonicalize('x*y=z*(y*(x*w))'),
        canonicalize('x*y=z*((w*y)*z)'),
        canonicalize('x*y=z*((z*w)*u)'),
        canonicalize('x*y=y*((z*z)*w)'),
        canonicalize('x*y=z*((z*x)*z)'),
    },
    square_right_sources={
        canonicalize('x=y*(x*x)'),
        canonicalize('x=(y*x)*(y*x)'),
        canonicalize('x=(y*(y*z))*(w*x)'),
        canonicalize('x=(y*(y*x))*(z*x)'),
    },
    square_right_targets={
        canonicalize('x=((x*y)*x)*(z*x)'),
        canonicalize('x=y*(z*(w*(u*x)))'),
        canonicalize('x*y=z*(y*(w*y))'),
    },
    square_left_sources={
        canonicalize('x=(x*x)*y'),
        canonicalize('x=(x*y)*(z*z)'),
    },
    square_left_targets={
        canonicalize('x*x=x*((y*z)*w)'),
    },
    c887_sources={
        canonicalize('x=y*((x*y)*(z*z))'),
        canonicalize('x=y*(((z*z)*x)*y)'),
        canonicalize('x=(y*y)*(z*(x*z))'),
        canonicalize('x=((y*x)*y)*(z*z)'),
        canonicalize('x=(y*(x*(z*z)))*y'),
        canonicalize('x=((y*y)*(z*x))*z'),
    },
    c887_targets={
        canonicalize('x=x*(((x*y)*x)*y)'),
    },
    left_generic_enabled=True,
    left_generic_require_x_absent=True,
    right_generic_enabled=False,
    right_generic_require_x_absent=False,
)


PROFILES = {
    GRAPH_V4.name: GRAPH_V4,
    GRAPH_V7.name: GRAPH_V7,
}


def get_profile(profile_name: str = 'graph_v4') -> CheatsheetProfile:
    try:
        return PROFILES[profile_name]
    except KeyError as exc:
        available = ', '.join(sorted(PROFILES))
        raise ValueError(f'Unknown profile {profile_name!r}. Available: {available}') from exc


def is_left_family(eq: str, profile: CheatsheetProfile) -> bool:
    lhs, rhs = parse_sides(eq)
    if canonicalize(eq) in profile.left_family:
        return True
    if not profile.left_generic_enabled:
        return False
    if not is_bare_var(lhs) or not rhs.startswith(lhs + '*'):
        return False
    expr = rhs[2:]
    first_var = leftmost_var(expr)
    if profile.left_generic_require_x_absent and lhs in get_vars(expr):
        return False
    return first_var is not None and first_var != lhs and len(re.findall(first_var, expr)) == 1


def is_right_family(eq: str, profile: CheatsheetProfile) -> bool:
    lhs, rhs = parse_sides(eq)
    if canonicalize(eq) in profile.right_family:
        return True
    if not profile.right_generic_enabled:
        return False
    if not is_bare_var(lhs) or not rhs.endswith('*' + lhs):
        return False
    expr = rhs[:-2]
    first_var = leftmost_var(expr)
    if profile.right_generic_require_x_absent and lhs in get_vars(expr):
        return False
    return first_var is not None and first_var != lhs and len(re.findall(first_var, expr)) == 1


def is_const_family(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.const_family


def is_square_right_family(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.square_right_sources


def is_square_left_family(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.square_left_sources


def is_c887_family(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.c887_sources


def square_right_target_matches(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.square_right_targets


def square_left_target_matches(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.square_left_targets


def c887_target_matches(eq: str, profile: CheatsheetProfile) -> bool:
    return canonicalize(eq) in profile.c887_targets


def predict_implication(e1: str, e2: str, profile_name: str = 'graph_v4') -> tuple[bool | None, str]:
    profile = get_profile(profile_name)

    if same_law(e1, e2):
        return True, 'same_law'
    if is_singleton_forcing(e1):
        return True, 'singleton'
    if e2 == 'x=x':
        return True, 'trivial'
    if is_left_family(e1, profile):
        return left_proj_satisfies(e2), 'left_family'
    if is_right_family(e1, profile):
        return right_proj_satisfies(e2), 'right_family'
    if is_const_family(e1, profile):
        return const_satisfies(e2), 'const_family'
    if is_c887_family(e1, profile) and c887_target_matches(e2, profile):
        return True, 'c887_family'
    if is_square_right_family(e1, profile) and square_right_target_matches(e2, profile):
        return True, 'square_family'
    if is_square_left_family(e1, profile) and square_left_target_matches(e2, profile):
        return True, 'square_family'
    if left_proj_satisfies(e1) and not left_proj_satisfies(e2):
        return False, 'counter_lp'
    if right_proj_satisfies(e1) and not right_proj_satisfies(e2):
        return False, 'counter_rp'
    if const_satisfies(e1) and not const_satisfies(e2):
        return False, 'counter_const'
    if parity_satisfies(e1) and not parity_satisfies(e2):
        return False, 'counter_xor'
    lhs2, rhs2 = parse_sides(e2)
    if lhs2 != rhs2 and is_bare_var(lhs2) and is_bare_var(rhs2):
        return False, 'singleton_target'
    if is_balanced(e1) and not is_balanced(e2):
        return False, 'balance'
    return None, 'unsolved'


def family_name(eq: str, profile_name: str = 'graph_v4') -> str:
    profile = get_profile(profile_name)

    if is_singleton_forcing(eq):
        return 'singleton'
    if is_left_family(eq, profile):
        return 'left_family'
    if is_right_family(eq, profile):
        return 'right_family'
    if is_const_family(eq, profile):
        return 'const_family'
    if is_c887_family(eq, profile):
        return 'c887_family'
    if is_square_right_family(eq, profile) or is_square_left_family(eq, profile):
        return 'square_family'
    return 'other'
