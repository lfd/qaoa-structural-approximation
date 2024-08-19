Instance Batches
================

If you have to run experiments on multiple problem instances, *instance batches* are your friend. Simply put an instance batch is a collection of problem instances. In order to manage batches across large instance pools spread out over the file system you can declare them in *batch files*. 

Loading Batches
---------------

All you have to do in order to load a batch is to call the `batch.load("path/batch_file")` function with the path to the corresponding batch file.

```python
import a2.batch

instance_paths = a2.batch.load("path/to/batch_file")

```

Batch Files
-----------

Batch files are used do index all instances contained in the batch. The real power of these files comes from two features *nested batches* and the possibility to *include batch files*. A example may look like this:

```JSON
{
  "dir": "./some/path",
  
  "include":
  [
    "path/to_other/batch_file1",
    "path/to_other/batch_file2"
  ],

  "instances":
  [
    "instance1.cnf",
    "instance2.cnf"
  ],

  "batches": 
  [
    {
      "dir": "./nested/path",
      "instances":
      [
        "instanec11.cnf", 
        "instance22.cnf"
      ]
    }
  ]
}

```
A complete grammar is defined further below. The main components of a batch files are *batch objects*. Possible fields of batch objects are:

dir
: The base directory for all contained paths. Consider the example above. The path `instance1.cnf` will be expanded to `./some/path/instance1.cnf`. 
: If the base path of a batch is relative (e.g. `./path`) it is always relative to its parent batch (e.g. `./nested/path` will be extended to `./some/path/nested/path`). In case of root batches (highest level in batch file) relative base paths are relative to the file location.
: If no `"dir:"` is specified, the base path of the parent batch is inherited (no `"dir:"` is similar to `"dir": "."`).

include
: Here you can list paths to other batch files, which than will be included to the current batch.

instances
: This is the actual list of instance paths.

batches
: Instance batches can contain other (nested) instance batches. This allows you to structure your batch files much more nicely (see nested base paths).
 
---
### Grammar
The complete grammar of a batch file is defined by:

```
<file> ::= <batch>
<batch> ::= '{' <fields> '}'
<fields> ::= <field> 
             | ',' <fields> 
<field> ::= <directory>
            | <instance list> 
            | <include list> 
            | <batch list>
<directory> ::= '"dir":' <Path>
<instance list> ::= '"instances": [' <paths> ']'
<include list> ::= '"include": [' <paths> ']'
<batch list> ::= '"batches": [' <batches> ']'
<paths> ::= <path> | ',' <paths>
<batches> ::= <batch> | ',' <batches>
```
---
