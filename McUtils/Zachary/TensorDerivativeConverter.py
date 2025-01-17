
import abc, numpy as np, typing

__all__ = [
    'TensorDerivativeConverter',
    'TensorExpansionTerms',
    'TensorExpression'
]


class TensorExpression:
    def __init__(self, expr:'TensorExpression.Term', vars:dict=None):
        self.expr = expr
        self.vars = vars
    def eval(self, subs:dict=None):
        if subs is None:
            subs = self.vars
        if subs is None:
            subs = {}
        prims = self.primitives
        cache = {}
        names = {p.name:p for p in prims}
        for k in subs.keys() & names.keys():
            p = names[k]
            v = subs[k]
            cache[p] = p._arr
            p._arr = v
        try:
            return self.expr.array
        finally:
            for p,v in cache.items():
                p._arr = v
    @property
    def primitives(self):
        return self.get_prims()
    def walk(self, callback):
        bfs_queue = [self.expr]
        visited = set()
        while bfs_queue:
            e = bfs_queue.pop()
            bfs_queue.extend(e.children)
            callback(e)
            visited.add(e)
    def get_prims(self):
        kids = set()
        def add_if_prim(e):
            if len(e.children) == 0:
                kids.add(e)
        self.walk(add_if_prim)
        return kids
    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.expr)
    
    class Term(metaclass=abc.ABCMeta):
        def __init__(self, array=None, name=None):
            self._arr = array
            self.name = name
        @abc.abstractmethod
        def get_children(self) -> 'Iterable[TensorExpression.Term]':
            raise NotImplementedError("base class")
        @property
        def children(self):
            return self.get_children()
        @abc.abstractmethod
        def deriv(self) -> 'TensorExpression.Term':
            raise NotImplementedError("base class")
        def dQ(self):
            new_term = self.deriv()
            if self.name is not None and isinstance(new_term, TensorExpression.Term):
                new_term.name = 'dQ({})'.format(self.name)
            return new_term
        @abc.abstractmethod
        def asarray(self, **kwargs) -> np.ndarray:
            raise NotImplementedError("base class")
        @property
        def array(self):
            if self._arr is None:
                try:
                    self._arr = self.asarray()
                except TensorExpansionError:
                    raise
                except Exception as e:
                    raise TensorExpansionError('failed to convert {} to an array'.format(self))
            return self._arr
        @array.setter
        def array(self, arr):
            self._arr = arr
        @abc.abstractmethod
        def rank(self) -> int:
            raise NotImplementedError("base class")
        @property
        def ndim(self):
            return self.rank()
        @abc.abstractmethod
        def to_string(self) -> str:
            raise NotImplementedError("base class")
        def __repr__(self):
            if self.name is None:
                return self.to_string()
            else:
                return self.name
        @abc.abstractmethod
        def reduce_terms(self, check_arrays=False) -> 'TensorExpression.Term':
            raise NotImplementedError("base class")
        def _check_simp(self, new):
            new._arr = None
            n2 = new.array
            if not np.allclose(self.array, n2):
                raise TensorExpansionError("bad simplification {} -> {}".format(self, new))
        def simplify(self, check_arrays=False):
            if check_arrays:
                arr = self.array
                self._arr = None
                red = self.reduce_terms(check_arrays=True)
                new = red.array
                if not np.allclose(arr, new):
                    raise TensorExpansionError("bad simplification {} -> {}".format(self, red))
                new = red
            else:
                new = self.reduce_terms()
            if isinstance(new, TensorExpression.Term):
                if new.name is None:
                    new.name = self.name
                if new._arr is None:
                    new._arr = self._arr
            return new
        def __add__(self, other):
            return TensorExpression.SumTerm(self, other)
        def __mul__(self, other):
            return TensorExpression.ScalingTerm(self, other)
        def __rmul__(self, other):
            return TensorExpression.ScalingTerm(self, other)
    
        def __pos__(self):
            return self
        def __neg__(self):
            return -1 * self
        def flip(self):
            raise NotImplementedError("base class")
    
        def divided(self):
            if self.ndim > 0:
                raise ValueError("term {} isn't a scalar".format(self))
            else:
                return TensorExpression.FlippedTerm(self)
        def __truediv__(self, other):
            if isinstance(other, TensorExpression.Term):
                return TensorExpression.ScalingTerm(self, other.divided())
            else:
                return TensorExpression.ScalingTerm(self, 1 / other)
        def __rtruediv__(self, other):
            if isinstance(other, TensorExpression.Term):
                return other.__truediv__(self)
            else:
                return TensorExpression.ScalingTerm(self.divided(), other)
    
        def dot(self, other, i, j):
            return TensorExpression.ContractionTerm(self, i, j, other)
    
        def shift(self, i, j):
            if i < 1 or j < 1 or i == j:
                return self
            else:
                return TensorExpression.AxisShiftTerm(self, i, j)
    
        def det(self):
            return TensorExpression.DeterminantTerm(self)
    
        def tr(self, axis1=1, axis2=2):
            return TensorExpression.TraceTerm(self, axis1=axis1, axis2=axis2)
    
        def inverse(self):
            return TensorExpression.InverseTerm(self)
    
        def __invert__(self):
            return self.inverse()
    
        def __hash__(self):
            return hash(str(self))
    
        def __eq__(self, other):
            return str(self) == str(other)
    
    class SumTerm(Term):
        def __init__(self, *terms: 'TensorExpression.Term', array=None):
            super().__init__(array=array)
            self.terms = terms
        def get_children(self):
            return self.terms
        def deriv(self):
            return type(self)(*(s.dQ() for s in self.terms))
    
        def asarray(self, print_terms=False):
            all_terms = [(i, s.asarray(print_terms=print_terms)) for i, s in enumerate(self.terms)]
            clean_terms = [s for s in all_terms if
                           not (isinstance(s[1], (int, float, np.integer, np.floating)) and s[1] == 0)]
            for s in clean_terms:
                if s[1].shape != clean_terms[0][1].shape:
                    raise Exception(
                        "this term is bad {} in {} (shape {} instead of shape {})".format(self.terms[s[0]], self,
                                                                                          s[1].shape,
                                                                                          clean_terms[0][1].shape
                                                                                          ))
            clean_terms = [c[1] for c in clean_terms]
            try:
                return np.sum(clean_terms, axis=0)
            except:
                raise Exception(clean_terms)
    
        def rank(self):
            return self.terms[0].ndim
    
        def reduce_terms(self, check_arrays=False):
            full_terms = []
            cls = type(self)
            for t in self.terms:
                t = t.simplify(check_arrays=check_arrays)
                if isinstance(t, cls):
                    full_terms.extend(t.terms)
                elif not (isinstance(t, (int, float, np.integer, np.floating)) and t == 0):
                    full_terms.append(t)
            full_terms = list(sorted(full_terms, key=lambda t: str(t)))  # canonical sorting is string sorting b.c. why not
            return type(self)(*full_terms, array=self._arr)
    
        def to_string(self):
            return '+'.join(str(x) for x in self.terms)
    
        def substitute(self, other):
            """substitutes other in to the sum by matching up all necessary terms"""
            if isinstance(other, TensorExpression.SumTerm):
                my_terms = list(self.terms)
                for t in other.terms:
                    i = my_terms.index(t)
                    my_terms = my_terms[:i] + my_terms[i + 1:]
                my_terms.append(other)
                return type(self)(*my_terms)
            else:
                my_terms = list(self.terms)
                i = my_terms.index(other)
                my_terms = my_terms[:i] + my_terms[i + 1:]
                my_terms.append(other)
                return type(self)(*my_terms)
    class ScalingTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', scaling, array=None):
            super().__init__(array=array)
            self.scaling = scaling
            self.term = term
        def get_children(self):
            return [self.scaling, self.term]
        def rank(self):
            if isinstance(self.scaling, TensorExpression.Term):
                scale_dim = self.scaling.ndim
            elif isinstance(self.scaling, np.ndarray):
                scale_dim = self.scaling.ndim
            else:
                scale_dim = 0
            return scale_dim + self.term.ndim
        def asarray(self, print_terms=False):
            scaling = self.scaling
            if isinstance(self.scaling, TensorExpression.Term):
                scaling = scaling.asarray(print_terms=print_terms)
            if isinstance(scaling, np.ndarray):
                term = self.term.asarray(print_terms=print_terms)
                if scaling.ndim > 0 and term.ndim > 0:
                    og_term_dim = term.ndim
                    for i in range(scaling.ndim):
                        term = np.expand_dims(term, -1)
                    for i in range(og_term_dim):
                        scaling = np.expand_dims(scaling, 0)
            else:
                term = self.term.asarray(print_terms=print_terms)
            return scaling * term
    
        def to_string(self):
            meh_1 = '({})'.format(self.scaling) if isinstance(self.scaling, TensorExpression.SumTerm) else self.scaling
            meh_2 = '({})'.format(self.term) if isinstance(self.term, TensorExpression.SumTerm) else self.term
            return '{}*{}'.format(meh_1, meh_2)
    
        def reduce_terms(self, check_arrays=False):
            scaling = self.scaling
            if isinstance(self.scaling, TensorExpression.Term):
                scaling = scaling.simplify(check_arrays=check_arrays)
            if isinstance(scaling, (int, float, np.integer, np.floating)) and scaling == 1:
                return self.term.simplify(check_arrays=check_arrays)
            elif (
                    (isinstance(scaling, (int, float, np.integer, np.floating)) and scaling == 0)
                    or
                    (isinstance(self.term, (int, float, np.integer, np.floating)) and self.term == 0)
            ):
                return 0
            else:
                return type(self)(self.term.simplify(check_arrays=check_arrays), scaling, array=self._arr)
    
        def deriv(self):
            term = type(self)(self.term.dQ(), self.scaling)
            if isinstance(self.scaling, TensorExpression.Term):
                ugh2 = type(self)(self.term, self.scaling.dQ())
                term += ugh2
            return term
    class PowerTerm(Term):
        """
        Represents x^n. Only can get valid derivatives for scalar terms. Beware of that.
        """
        def __init__(self, term: 'TensorExpression.Term', pow, array=None):
            super().__init__(array=array)
            self.term = term
            self.pow = pow
            if self.term.ndim > 0:
                raise ValueError("can't do this pops")
        def get_children(self):
            return [self.pow, self.term]
    
        def rank(self):
            return self.term.rank()
    
        def asarray(self, print_terms=False):
            wat = self.term.asarray(print_terms=print_terms)
            out = wat ** self.pow
            return out
    
        def to_string(self):
            return '({}**{})'.format(self.term, self.pow)
    
        def reduce_terms(self, check_arrays=False):
            if self.pow == 1:
                return self.term.simplify(check_arrays=check_arrays)
            elif self.pow == 0:
                return 1
            elif self.pow == -1:
                return TensorExpression.FlippedTerm(self.term.simplify(check_arrays=True), array=self._arr)
            else:
                return TensorExpression.PowerTerm(self.term.simplify(check_arrays=check_arrays), self.pow,
                                                      array=self._arr)
    
        def deriv(self):
            return TensorExpression.ScalingTerm(
                self.pow * self.term.dQ(),
                TensorExpression.PowerTerm(self.term, self.pow - 1)
            )
    class FlippedTerm(PowerTerm):
        """
        Represents 1/x. Only can get valid derivatives for scalar terms. Beware of that.
        """
    
        def __init__(self, term: 'TensorExpression.Term', pow=-1, array=None):
            super().__init__(term, -1, array=array)
        def get_children(self):
            return [self.term]
    
        def to_string(self):
            return '1/{}'.format(self.term)
    
        def asarray(self, print_terms=False):
            out = 1 / self.term.asarray(print_terms=print_terms)
            return out
    
        def reduce_terms(self, check_arrays=False):
            if isinstance(self.term, TensorExpression.FlippedTerm):
                wat = self.term.term.simplify(check_arrays=check_arrays)
                if check_arrays: self._check_simp(wat)
                return wat
            else:
                return super().reduce_terms(check_arrays=check_arrays)
    class AxisShiftTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', start: int, end: int, array=None):
            super().__init__(array=array)
            self.term = term
            self.a = start
            self.b = end
        def get_children(self):
            return [self.term]
        def deriv(self):
            return type(self)(self.term.dQ(), self.a + 1, self.b + 1)
    
        def asarray(self, print_terms=False):
            t = self.term.asarray(print_terms=print_terms)
            if isinstance(t, (int, float, np.integer, np.floating)) and t == 0:
                return 0
            else:
                return np.moveaxis(self.term.array, self.a - 1, self.b - 1)
    
        def rank(self):
            return self.term.ndim
    
        def to_string(self):
            return '{{{}#{}->{}}}'.format(self.term, self.a, self.b)
    
        def reduce_terms(self, check_arrays=False):
            """We simplify over the possible swap classes"""
            cls = type(self)
            simp = self.term.simplify(check_arrays=check_arrays)
            sela = self.a
            selb = self.b
            if sela == selb:
                new = simp
                if check_arrays: self._check_simp(new)
            elif sela > selb:  # we flip this around
                new = cls(simp, selb, sela)
                for i in range(sela - selb - 1):
                    new = cls(new, selb, sela)
                new._arr = self._arr
                new = new.simplify(check_arrays=check_arrays)
                if check_arrays: self._check_simp(new)
            elif isinstance(simp, cls):
                otht = simp.term.simplify(check_arrays=check_arrays)
                otha = simp.a
                othb = simp.b
                if sela == othb:
                    if otha == selb:  # inverses although we shouldn't get here...
                        if otht._arr is None:
                            otht._arr = self._arr
                        new = otht
                    else:  # reduces to a single term
                        new_a = otha
                        new_b = selb
                        new = cls(otht, new_a, new_b, array=self._arr)
                        if check_arrays: self._check_simp(new)
                elif otha > sela:  # we needed to pick a convention...
                    new_sela = sela
                    new_selb = selb if selb < otha else selb + 1
                    other = cls(otht, new_sela, new_selb)
                    new_a = otha if otha > selb else otha - 1
                    new_b = othb if othb > selb else othb - 1
                    new = cls(other, new_a, new_b)
                    if check_arrays: self._check_simp(new)
                    if new._arr is None: new._arr = self._arr
                    return new
                elif otha == sela and othb == selb:
                    # check if we have enough iterates to get the identity
                    is_ident = True
                    for i in range(selb - sela):
                        if isinstance(otht, cls) and otht.a == sela and otht.b == selb:
                            otht = otht.term
                        else:
                            is_ident = False
                            break
                    if is_ident:
                        new = otht
                        if check_arrays:
                            self._check_simp(new)
                    else:
                        new = self
                else:
                    new = cls(simp, sela, selb)
            elif isinstance(simp, TensorExpression.SumTerm):
                new = TensorExpression.SumTerm(
                    *(x.shift(self.a, self.b).simplify(check_arrays=check_arrays) for x in simp.terms),
                    array=self._arr
                )
                if check_arrays:
                    self._check_simp(new)
            else:
                new = self
    
            return new
    class ContractionTerm(Term):
        def __init__(self, left: 'TensorExpression.Term',
                     i: typing.Union[int, typing.Iterable[int]],
                     j: typing.Union[int, typing.Iterable[int]],
                     right: 'TensorExpression.Term', array=None):
            super().__init__(array=array)
            self.left = left
            self.i = i
            self.j = j
            self.right = right
        def get_children(self):
            return [self.left, self.right]
    
        def asarray(self, print_terms=False):
            t1 = self.left.asarray(print_terms=print_terms)
            t2 = self.right.asarray(print_terms=print_terms)
            if isinstance(t1, (int, float, np.integer, np.floating)) and t1 == 0:
                return 0
            elif isinstance(t2, (int, float, np.integer, np.floating)) and t2 == 0:
                return 0
            else:
                # try:
                i = self.i
                if isinstance(i, (int, np.integer)):
                    i = i - 1
                else:
                    i = [x - 1 for x in i]
                j = self.j
                if isinstance(i, (int, np.integer)):
                    j = j - 1
                else:
                    j = [x - 1 for x in j]
                try:
                    return np.tensordot(t1, t2, axes=[i, j])
                except:
                    raise TensorExpansionError(
                        'failed to contract {}[{}]x{}[{}] for {} and {}'.format(t1.shape, i, t2.shape, j, self.left,
                                                                                self.right))
                # except (ValueError, IndexError):
                #     raise ValueError("failed to execute {}".format(self))
    
        def rank(self):
            return self.left.ndim + self.right.ndim - 2
    
        def deriv(self):
            return (
                    type(self)(self.left.dQ(),
                               self.i + 1 if isinstance(self.i, (int, np.integer)) else [x + 1 for x in self.i],
                               # not sure if this is right...
                               self.j,
                               self.right
                               ) + type(self)(
                self.left,
                self.i,
                self.j + 1 if isinstance(self.j, (int, np.integer)) else [x + 1 for x in self.j],
                self.right.dQ()
            ).shift(self.left.ndim - (0 if isinstance(self.j, (int, np.integer)) else len(self.j) - 1), 1)
            )
    
        def to_string(self):
            return '<{}:{},{}:{}>'.format(self.left, self.i, self.j, self.right)
    
        def reduce_terms(self, check_arrays=False):
            cls = type(self)
            left = self.left.simplify(check_arrays=check_arrays)
            right = self.right.simplify(check_arrays=check_arrays)
            if isinstance(right, TensorExpression.AxisShiftTerm):
                # I flip the names just so it agrees with my math...
                t = right.term
                i = right.a
                j = right.b
                a = self.i
                b = self.j
                n = left.ndim
                if b < i:
                    new = cls(left, a, b, t).shift(n - 2 + i, n - 2 + j)
                    if check_arrays:
                        self._check_simp(new)
                elif b < j:
                    new = cls(left, a, b + 1, t).shift(n - 1 + i, n - 2 + j)
                    if check_arrays:
                        self._check_simp(new)
                elif b == j:
                    new = cls(left, a, i, t)
                    if check_arrays:
                        self._check_simp(new)
                else:
                    new = cls(left, a, b, t).shift(n - 1 + i, n - 1 + j)
                    if check_arrays:
                        self._check_simp(new)
    
            elif isinstance(left, TensorExpression.AxisShiftTerm):
                # I flip the names just so it agrees with my math...
                t = left.term
                i = left.a
                j = left.b
                a = self.i
                b = self.j
                if a > j:
                    new = cls(t, a, b, right).shift(i, j)
                    if check_arrays:
                        self._check_simp(new)
                elif a == j:
                    new = cls(t, i, b, right)
                    if check_arrays:
                        self._check_simp(new)
                elif a >= i:
                    new = cls(t, a + 1, b, right).shift(i, j - 1)
                    if check_arrays:
                        self._check_simp(new)
                else:
                    new = cls(t, a, b, right).shift(i - 1, j - 1)
                    if check_arrays:
                        self._check_simp(new)
            elif isinstance(left, TensorExpression.SumTerm):
                new = TensorExpression.SumTerm(
                    *(cls(x, self.i, self.j, right).simplify(check_arrays=check_arrays) for x in left.terms),
                    array=self._arr
                )
                if check_arrays:
                    self._check_simp(new)
            elif isinstance(right, TensorExpression.SumTerm):
                new = TensorExpression.SumTerm(
                    *(cls(left, self.i, self.j, x).simplify(check_arrays=check_arrays) for x in right.terms),
                    array=self._arr
                )
                if check_arrays:
                    self._check_simp(new)
            # elif isinstance(self.left, QXTerm) and isinstance(self.right, XVTerm):
            #     new = BasicContractionTerm(self.left.terms, self.left.n, self.i, self.j, self.right.m,
            #                                                      array=self._arr)
            else:
                new = cls(self.left.simplify(check_arrays=check_arrays), self.i, self.j,
                          self.right.simplify(check_arrays=check_arrays), array=self._arr)
    
            if new._arr is None:
                new._arr = self._arr
    
            return new
    
    # fancier terms
    class InverseTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', array=None):
            super().__init__(array=array)
            self.term = term

        def get_children(self):
            return [self.term]
    
        def rank(self):
            return self.term.rank()
    
        def asarray(self, print_terms=False):
            arr = np.linalg.inv(self.term.asarray(print_terms=print_terms))
            if print_terms:
                print(self)
                print(arr)
            return arr
    
        def to_string(self):
            return '({}^-1)'.format(self.term)
    
        def reduce_terms(self, check_arrays=False):
            return type(self)(self.term.simplify(check_arrays=check_arrays), array=self._arr)
    
        def deriv(self):
            dq = self.term.dQ()
            sub = self.dot(dq, self.ndim, 2).shift(self.ndim, 1)  # self.dot(self.term.dQ(), self.ndim, 2)
            return -sub.dot(self, sub.ndim, 1)  # .shift(self.ndim, 1)
    class TraceTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', axis1=1, axis2=2, array=None):
            super().__init__(array=array)
            self.term = term
            self.axis1 = axis1
            self.axis2 = axis2

        def get_children(self):
            return [self.term]
    
        def rank(self):
            return self.term.ndim - 2
    
        def asarray(self, print_terms=False):
            arr = np.trace(self.term.asarray(print_terms=print_terms), axis1=self.axis1 - 1, axis2=self.axis2 - 1)
            if print_terms:
                print(self)
                print(arr)
            return arr
    
        def to_string(self):
            return 'Tr[{},{}+{}]'.format(self.term, self.axis1, self.axis2)
    
        def reduce_terms(self, check_arrays=False):
            simp = self.term.simplify(check_arrays=check_arrays)
            if isinstance(simp, TensorExpression.SumTerm):
                new = TensorExpression.SumTerm(
                    *(type(self)(t, axis1=self.axis1, axis2=self.axis2) for t in simp.terms),
                    array=self._arr
                )
                if check_arrays: self._check_simp(new)
            # elif isinstance(simp, AxisShiftTerm):
            #     # wait this is completely wrong...?
            #
            #     sub = type(self)(simp.term, axis1=self.axis1, axis2=self.axis2)
            #     new = AxisShiftTerm(
            #         type(self)(simp.term, axis1=self.axis1, axis2=self.axis2),
            #         simp.a,
            #         simp.b,
            #         array=self._arr
            #     )
            #     if check_arrays: self._check_simp(new)
            else:
                new = type(self)(simp, axis1=self.axis1, axis2=self.axis2, array=self._arr)
            return new
    
        def deriv(self):
            wat = self.term.dQ()
            return type(self)(wat, axis1=self.axis1 + 1, axis2=self.axis2 + 1)
    class DeterminantTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', array=None):
            super().__init__(array=array)
            self.term = term
        def get_children(self):
            return [self.term]
        def rank(self):
            return 0
        def asarray(self, print_terms=False):
            return np.linalg.det(self.term.asarray(print_terms=print_terms))
        def to_string(self):
            return '|{}|'.format(self.term)
        def reduce_terms(self, check_arrays=False):
            return type(self)(self.term.simplify(check_arrays=check_arrays), array=self._arr)
        def deriv(self):
            inv_dot = TensorExpression.InverseTerm(self.term).dot(
                self.term.dQ(),
                self.term.ndim,
                2
            )
            if self.term.ndim > 1:
                inv_dot = inv_dot.shift(self.term.ndim, 1)
            # print(inv_dot)
            tr = TensorExpression.TraceTerm(
                inv_dot,
                axis1=2,
                axis2=inv_dot.ndim
            ) * self
            # if self.term.ndim > 2:
            #     tr = tr.shift(self.term.ndim-1, 1)
            return tr
    class VectorNormTerm(Term):
        def __init__(self, term: 'TensorExpression.Term', array=None, axis=-1):
            super().__init__(array=array)
            self.term = term
            self.axis = axis
        def get_children(self):
            return [self.term]
        def rank(self):
            return self.term.rank() - 1
        def asarray(self, print_terms=False):
            return np.linalg.norm(self.term.asarray(print_terms=print_terms), axis=self.axis)
        def to_string(self):
            return '||{}||'.format(self.term)
        def reduce_terms(self, check_arrays=False):
            return type(self)(self.term.simplify(check_arrays=check_arrays), array=self._arr)
        def deriv(self):
            return self.term / self
    
    class CoordinateVectorTerm(Term):
        def __init__(self, name='x', array=None):
            super().__init__(array=array)
            self.name = name
        def get_children(self):
            return []
        def rank(self):
            return 1
        def asarray(self, print_terms=False):
            if self._arr is None:
                raise NotImplementedError("Need explicit vector values for this to work")
            else:
                return self._arr
        def reduce_terms(self, check_arrays=False):
            return self
        def to_string(self):
            return self.name
        def deriv(self):
            if self._arr is not None:
                arr = np.diag(self.array)
            else:
                arr = None
            return TensorExpression.ConstantMatrixTerm(name='dQ({})'.format(self.name), array=arr)
    class ConstantMatrixTerm(Term):
        def __init__(self, name='I', array=None):
            super().__init__(array=array)
            self.name = name
        def get_children(self):
            return []
        def rank(self):
            return 2
        def asarray(self, print_terms=False):
            if self._arr is None:
                raise NotImplementedError("Need explicit vector values for this to work")
            else:
                return self._arr
        def reduce_terms(self, check_arrays=False):
            return self
        def to_string(self):
            return self.name
        def deriv(self):
            return 0
    class ScalarFunctionTerm(Term):
        def __init__(self, term, name='f', f=None, array=None, derivative_order=0):
            super().__init__(array=array)
            self.term = term
            self.fname = name
            if f is not None and not isinstance(f, dict):
                f = {'function':f, 'derivatives':None}
            self.func = f
            self.deriv_order = derivative_order
        def get_children(self):
            return [self.term]
        def rank(self):
            return 0
        def asarray(self, print_terms=False):
            if self.func is None:
                raise NotImplementedError("need concrete function to evaluate")
            if self.deriv_order == 0:
                f = self.func['function']
                if f is None:
                    raise NotImplementedError("need concrete function to evaluate")
                return f(self.term.array)
            else:
                df = self.func['derivatives']
                if df is None:
                    raise NotImplementedError("need concrete derivatives to evaluate")
                return df(self.deriv_order)(self.term.array)
        def to_string(self):
            return (
                "{}({})".format(self.fname, self.term)
                if self.deriv_order == 0 else
                "{}[{}']({})".format(self.fname, self.deriv_order, self.term)
            )
        def reduce_terms(self, check_arrays=False):
            return type(self)(self.term.simplify(check_arrays=check_arrays),
                              name=self.fname, f=self.func, array=self._arr,
                              derivative_order=self.deriv_order
                              )
        def deriv(self):
            return self.term.deriv() * type(self)(
                self.term, name=self.fname, f=self.func, array=None,
                derivative_order=self.deriv_order+1
            )
    class PolynomialTerm(Term):
        def __init__(self, expansion:'Taylor.FunctionExpansion', coords:'TensorExpression.CoordinateVectorTerm'=None, array=None):
            super().__init__(array=array)
            self.expansion = expansion
            self.coords = coords
        def get_children(self):
            return [self.coords]
        def rank(self):
            return 0
        def asarray(self, print_terms=False):
            return self.expansion(self.coords.array)
        def to_string(self):
            return "{}({})".format(self.expansion, self.coords)
        def deriv(self):
            return type(self)(self.expansion.deriv(), coords=self.coords)
        def reduce_terms(self, check_arrays=False):
            return self

class TensorExpansionError(Exception):
    ...
class TensorExpansionTerms:
    """
    A friend of DumbTensor which exists
    to not only make the tensor algebra suck less but also
    to make it automated by making use of some simple rules
    for expressing derivatives specifically in the context of
    doing the coordinate transformations we need to do.
    Everything here is 1 indexed since that's how I did the OG math
    """
    def __init__(self, qx_terms, xv_terms, qxv_terms=None, base_qx=None, base_xv=None,
                 q_name='Q',
                 v_name='V'
                 ):
        """
        :param qx_terms:
        :type qx_terms: Iterable[np.ndarray]
        :param xv_terms:
        :type xv_terms: Iterable[np.ndarray]
        """
        self.qx_terms = qx_terms
        self.xv_terms = [0.]*len(qx_terms) if xv_terms is None else xv_terms
        self.qxv_terms = qxv_terms
        self.base_qx = base_qx
        self.base_xv = base_xv
        self.q_name = q_name
        self.v_name = v_name
    def QX(self, n):
        return self.QXTerm(self, n)
    def XV(self, m):
        return self.XVTerm(self, m)
    def QXV(self, n, m):
        return self.QXVTerm(self,n,  m)

    class QXTerm(TensorExpression.Term):
        def __init__(self, terms: 'TensorExpansionTerms', n: int, array=None):
            super().__init__(array=array)
            self.terms = terms
            self.n = n
        def get_children(self):
            return []
        def deriv(self):
            return type(self)(self.terms, self.n + 1)
        def asarray(self, print_terms=False):
            if self.n == 0:
                return self.terms.base_qx
            else:
                return self.terms.qx_terms[self.n - 1]
        def rank(self):
            if isinstance(self.array, (int, float, np.integer, np.floating)) and self.array == 0:
                return self.n + 1
            else:
                return self.array.ndim

        def to_string(self):
            return '{}[{}]'.format(self.terms.q_name, self.n)

        def reduce_terms(self, check_arrays=False):
            return self
    class XVTerm(TensorExpression.Term):
        def __init__(self, terms: 'TensorExpansionTerms', m: int, array=None):
            super().__init__(array=array)
            self.terms = terms
            self.m = m
        def get_children(self):
            return []
        def deriv(self):
            mixed_terms = self.terms.qxv_terms
            if (
                    mixed_terms is not None
                    and self.m > 0
                    and len(mixed_terms) > 0
                    # and mixed_terms[0] is not None
                    and len(mixed_terms[0]) >= self.m
                    and mixed_terms[0][self.m - 1] is not None
            ):
                return self.terms.QXV(1, self.m)
            else:
                return TensorExpression.ContractionTerm(self.terms.QX(1), 2, 1, self.terms.XV(self.m + 1))
        def asarray(self, print_terms=False):
            if self.m == 0:
                return self.terms.base_qx
            else:
                return self.terms.xv_terms[self.m - 1]
        def rank(self):
            if isinstance(self.array, (int, float, np.integer, np.floating)) and self.array == 0:
                return self.m
            else:
                return self.array.ndim
        def to_string(self):
            return '{}[{}]'.format(self.terms.v_name, self.m)
        def reduce_terms(self, check_arrays=False):
            return self
    class QXVTerm(TensorExpression.Term):
        def __init__(self, terms: 'TensorExpansionTerms', n: int, m: int, array=None):
            super().__init__(array=array)
            self.terms = terms
            self.n = n
            self.m = m
        def get_children(self):
            return []
        def deriv(self):
            return type(self)(self.terms, self.n + 1, self.m)

        def asarray(self, print_terms=False):
            return self.terms.qxv_terms[self.n - 1][self.m - 1]

        def rank(self):
            if isinstance(self.array, (int, float, np.integer, np.floating)) and self.array == 0:
                return self.n + self.m
            else:
                return self.array.ndim

        def to_string(self):
            return '{}{}[{},{}]'.format(self.terms.q_name, self.terms.v_name, self.n, self.m)

        def reduce_terms(self, check_arrays=False):
            return self
    class BasicContractionTerm(TensorExpression.Term):
        """
        Special case tensor contraction term between two elements of the
        tensor expansion terms.
        """

        def __init__(self, terms: 'TensorExpansionTerms', n: int, i: int, j: int, m: int, array=None):
            super().__init__(array=array)
            self.terms = terms
            self.n = n
            self.m = m
            self.i = i
            self.j = j

        def deriv(self):
            return TensorExpression.SumTerm(
                type(self)(
                    self.terms,
                    self.n + 1,
                    self.i + 1,
                    self.j,
                    self.m
                ),
                TensorExpression.ContractionTerm(
                    self.terms.QX(1),
                    2,
                    self.n,
                    type(self)(
                        self.terms,
                        self.n,
                        self.i,
                        self.j + 1,
                        self.m + 1
                    )
                )
            )

        def asarray(self, print_terms=False):
            arr = np.tensordot(self.terms.qx_terms[self.n - 1], self.terms.xv_terms[self.m - 1], axes=[self.i, self.j])
            if print_terms:
                print(self)
                print(arr)
            return arr

        def rank(self):
            return self.terms.qx_terms[self.n - 1].ndim + self.terms.xv_terms[self.m - 1].ndim - 2

        def to_string(self):
            return '<Q[{}]:{},{}:V[{}]>'.format(self.n, self.i, self.j, self.m)

        def reduce_terms(self, check_arrays=False):
            return self

class TensorDerivativeConverter:
    """
    A class that makes it possible to convert expressions
    involving derivatives in one coordinate system in another
    """

    TensorExpansionError=TensorExpansionError

    #TODO: add way to not recompute terms over and over
    def __init__(self, jacobians, derivatives=None,
                 mixed_terms=None,
                 jacobians_name='Q',
                 values_name='V'
                 ):
        """

        :param jacobians: The Jacobian and higher-order derivatives between the coordinate systems
        :type jacobians: Iterable[np.ndarray]
        :param derivatives: Derivatives of some quantity in the original coordinate system
        :type derivatives: Iterable[np.ndarray]
        :param mixed_terms: Mixed derivatives of some quantity involving the new and old coordinates
        :type mixed_terms: Iterable[Iterable[None | np.ndarray]]
        """

        if derivatives is None:
            derivatives = [0] * len(jacobians)

        self.terms = TensorExpansionTerms(jacobians, derivatives, qxv_terms=mixed_terms, q_name=jacobians_name, v_name=values_name)

    def convert(self, order=None, print_transformations=False, check_arrays=False):

        if order is None:
            order = len(self.terms.qx_terms)

        if order < 0:
            raise ValueError("cannot convert derivatives between coordinates systems to order 0")

        arrays = []
        deriv = self.terms.QX(1).dot(self.terms.XV(1), 2, 1)
        arrays.append(deriv.array)

        for i in range(2, order+1):
            # print(">>>>>", deriv)
            deriv = deriv.dQ().simplify(check_arrays=check_arrays) # there's an occasional issue with shift simplifications I think...
            if print_transformations:
                print(">> order: ", i, deriv)
            arrays.append(deriv.array)

        return arrays