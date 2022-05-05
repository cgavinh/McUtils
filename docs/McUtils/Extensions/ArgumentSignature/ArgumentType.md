## <a id="McUtils.Extensions.ArgumentSignature.ArgumentType">ArgumentType</a> 
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L23)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L23?message=Update%20Docs)]
</div>

Defines a general purpose `ArgumentType` so that we can easily manage complicated type specs
The basic idea is to define a hierarchy of types that can then convert themselves down to
a `ctypes`-style spec as well as a C++ argument spec so that we can enable `SharedLibraryFunction`
to use either the basic `ctypes` FFI or a more efficient, but fragile system based off of extension modules.
This will be explicitly overridden by the `PrimitiveType`, `ArrayType` and `PointerType` subclasses that provide
the actual useable classes.
I'd really live to be integrate with what's in the `typing` module to be able to reuse that type-inference machinery

<div class="collapsible-section">
 <div class="collapsible-section collapsible-section-header" markdown="1">
 
### <a class="collapse-link" data-toggle="collapse" href="#methods">Methods and Properties</a> <a class="float-right" data-toggle="collapse" href="#methods"><i class="fa fa-chevron-down"></i></a>

 </div>
 <div class="collapsible-section collapsible-section-body collapse" id="methods" markdown="1">

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.ctypes_type" class="docs-object-method">&nbsp;</a> 
```python
@property
ctypes_type(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L?message=Update%20Docs)]
</div>

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.cpp_type" class="docs-object-method">&nbsp;</a> 
```python
@property
cpp_type(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L?message=Update%20Docs)]
</div>

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.types" class="docs-object-method">&nbsp;</a> 
```python
@property
types(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L?message=Update%20Docs)]
</div>

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.dtypes" class="docs-object-method">&nbsp;</a> 
```python
@property
dtypes(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L?message=Update%20Docs)]
</div>

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.isinstance" class="docs-object-method">&nbsp;</a> 
```python
isinstance(self, arg): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L50)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L50?message=Update%20Docs)]
</div>

<a id="McUtils.Extensions.ArgumentSignature.ArgumentType.cast" class="docs-object-method">&nbsp;</a> 
```python
cast(self, arg): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Extensions/ArgumentSignature.py#L53)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L53?message=Update%20Docs)]
</div>

 </div>
</div>




___

[Edit Examples](https://github.com/McCoyGroup/McUtils/edit/gh-pages/ci/examples/McUtils/Extensions/ArgumentSignature/ArgumentType.md) or 
[Create New Examples](https://github.com/McCoyGroup/McUtils/new/gh-pages/?filename=ci/examples/McUtils/Extensions/ArgumentSignature/ArgumentType.md) <br/>
[Edit Template](https://github.com/McCoyGroup/McUtils/edit/gh-pages/ci/docs/McUtils/Extensions/ArgumentSignature/ArgumentType.md) or 
[Create New Template](https://github.com/McCoyGroup/McUtils/new/gh-pages/?filename=ci/docs/templates/McUtils/Extensions/ArgumentSignature/ArgumentType.md) <br/>
[Edit Docstrings](https://github.com/McCoyGroup/McUtils/edit/master/Extensions/ArgumentSignature.py#L23?message=Update%20Docs)