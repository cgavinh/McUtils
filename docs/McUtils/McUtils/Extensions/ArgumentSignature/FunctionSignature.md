## <a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature">FunctionSignature</a>
Defines a function signature for a C-level caller.
To be used inside `SharedLibraryFunction` and things to manage the core interface.

### Properties and Methods
<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.__init__" class="docs-object-method">&nbsp;</a>
```python
__init__(self, name, *args, return_type=None): 
```

- `name`: `str`
    >the name of the function
- `args`: `Iterable[ArgumentType]`
    >the arguments passed to the function
- `return_type`: `ArgumentType | None`
    >the return type of the function

<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.build_argument" class="docs-object-method">&nbsp;</a>
```python
build_argument(self, argtup, which=None): 
```
Converts an argument tuple into an Argument object
- `argtup`: `Any`
    >No description...
- `:returns`: `_`
    >No description...

<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.args" class="docs-object-method">&nbsp;</a>
```python
@property
args(self): 
```

<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.return_type" class="docs-object-method">&nbsp;</a>
```python
@property
return_type(self): 
```

<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.cpp_signature" class="docs-object-method">&nbsp;</a>
```python
@property
cpp_signature(self): 
```

<a id="McUtils.McUtils.Extensions.ArgumentSignature.FunctionSignature.__repr__" class="docs-object-method">&nbsp;</a>
```python
__repr__(self): 
```

### Examples