## <a id="McUtils.Scaffolding.Jobs.Job">Job</a> 
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L18)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L18?message=Update%20Docs)]
</div>

A job object to support simplified run scripting.
Provides a `job_data` checkpoint file that stores basic
data about job runtime and stuff, as well as a `logger` that
makes it easy to plug into a run time that supports logging

<div class="collapsible-section">
 <div class="collapsible-section collapsible-section-header" markdown="1">
 
### <a class="collapse-link" data-toggle="collapse" href="#methods">Methods and Properties</a> <a class="float-right" data-toggle="collapse" href="#methods"><i class="fa fa-chevron-down"></i></a>

 </div>
 <div class="collapsible-section collapsible-section-body collapse" id="methods" markdown="1">

```python
default_job_file: str
default_log_file: str
```
<a id="McUtils.Scaffolding.Jobs.Job.__init__" class="docs-object-method">&nbsp;</a> 
```python
__init__(self, job_dir, job_file=None, logger=None, parallelizer=None, job_parameters=None): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L27)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L27?message=Update%20Docs)]
</div>

<a id="McUtils.Scaffolding.Jobs.Job.from_config" class="docs-object-method">&nbsp;</a> 
```python
from_config(config_location=None, job_file=None, logger=None, parallelizer=None, job_parameters=None): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L45)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L45?message=Update%20Docs)]
</div>

<a id="McUtils.Scaffolding.Jobs.Job.load_checkpoint" class="docs-object-method">&nbsp;</a> 
```python
load_checkpoint(self, job_file): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L60)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L60?message=Update%20Docs)]
</div>

Loads the checkpoint we'll use to dump params
- `job_file`: `Any`
    >No description...
- `:returns`: `_`
    >No description...

<a id="McUtils.Scaffolding.Jobs.Job.load_logger" class="docs-object-method">&nbsp;</a> 
```python
load_logger(self, log_spec): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L74)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L74?message=Update%20Docs)]
</div>

Loads the appropriate logger
- `log_spec`: `str | dict`
    >No description...
- `:returns`: `_`
    >No description...

<a id="McUtils.Scaffolding.Jobs.Job.load_parallelizer" class="docs-object-method">&nbsp;</a> 
```python
load_parallelizer(self, par_spec): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L104)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L104?message=Update%20Docs)]
</div>

Loads the appropriate parallelizer.
        If something other than a dict is passed,
        tries out multiple specs sequentially until it finds one that works
- `log_spec`: `dict`
    >No description...
- `:returns`: `_`
    >No description...

<a id="McUtils.Scaffolding.Jobs.Job.path" class="docs-object-method">&nbsp;</a> 
```python
path(self, *parts): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L130)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L130?message=Update%20Docs)]
</div>


- `parts`: `str`
    >No description...
- `:returns`: `_`
    >No description...

<a id="McUtils.Scaffolding.Jobs.Job.working_directory" class="docs-object-method">&nbsp;</a> 
```python
@property
working_directory(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L?message=Update%20Docs)]
</div>

<a id="McUtils.Scaffolding.Jobs.Job.__enter__" class="docs-object-method">&nbsp;</a> 
```python
__enter__(self): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L151)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L151?message=Update%20Docs)]
</div>

<a id="McUtils.Scaffolding.Jobs.Job.__exit__" class="docs-object-method">&nbsp;</a> 
```python
__exit__(self, exc_type, exc_val, exc_tb): 
```
<div class="docs-source-link" markdown="1">
[[source](https://github.com/McCoyGroup/McUtils/blob/master/Scaffolding/Jobs.py#L165)/[edit](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L165?message=Update%20Docs)]
</div>

 </div>
</div>




___

[Edit Examples](https://github.com/McCoyGroup/McUtils/edit/gh-pages/ci/examples/McUtils/Scaffolding/Jobs/Job.md) or 
[Create New Examples](https://github.com/McCoyGroup/McUtils/new/gh-pages/?filename=ci/examples/McUtils/Scaffolding/Jobs/Job.md) <br/>
[Edit Template](https://github.com/McCoyGroup/McUtils/edit/gh-pages/ci/docs/McUtils/Scaffolding/Jobs/Job.md) or 
[Create New Template](https://github.com/McCoyGroup/McUtils/new/gh-pages/?filename=ci/docs/templates/McUtils/Scaffolding/Jobs/Job.md) <br/>
[Edit Docstrings](https://github.com/McCoyGroup/McUtils/edit/master/Scaffolding/Jobs.py#L18?message=Update%20Docs)