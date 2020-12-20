## <a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction">SharedLibraryFunction</a>
An object that provides a way to call into a shared library function

### Properties and Methods
```python
InDir: type
```
<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.__init__" class="docs-object-method">&nbsp;</a>
```python
__init__(self, shared_library, signature, docstring=None, call_directory=None): 
```

- `shared_library`: `str |`
    >the path to the shared library file you want to use
- `function_signature`: `FunctionSignature`
    >the signature of the function to load
- `call_directory`: `str`
    >the directory for calling
- `docstring`: `str`
    >the docstring for the function

<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.lib" class="docs-object-method">&nbsp;</a>
```python
@property
lib(self): 
```

<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.initialize" class="docs-object-method">&nbsp;</a>
```python
initialize(self): 
```

<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.doc" class="docs-object-method">&nbsp;</a>
```python
doc(self): 
```

<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.__repr__" class="docs-object-method">&nbsp;</a>
```python
__repr__(self): 
```

<a id="McUtils.McUtils.Extensions.SharedLibraryManager.SharedLibraryFunction.call" class="docs-object-method">&nbsp;</a>
```python
call(self, **kwargs): 
```
Calls the function we loaded.
        This will be parallelized out to handle more complicated usages.
- `kwargs`: `Any`
    >No description...
- `:returns`: `_`
    >No description...

### Examples