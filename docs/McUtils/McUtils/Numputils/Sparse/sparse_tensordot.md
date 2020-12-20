# <a id="McUtils.McUtils.Numputils.Sparse.sparse_tensordot">sparse_tensordot</a>

Defines a version of tensordot that uses sparse arrays, adapted from the sparse package on PyPI

```python
sparse_tensordot(a, b, axes=2): 
```

- `a`: `SparseArray | sp.spmatrix | np.ndarray`
    >the array to contract from
- `b`: `SparseArray | sp.spmatrix | np.ndarray`
    >the array to contract with
- `axes`: `int | Iterable[int]`
    >the axes to contract along
- `:returns`: `_`
    >No description...

###Examples: