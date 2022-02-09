# slate-pl
Slate Programming Language

### Future Slate Features
- Function Overloading
- Enums
- Bignums (Arbitrary length integers)

## Importing and Exporting
Given the following directory structure:
```
.
├── other_modules
│   ├── module3.slt
│   └── module4.slt
├── module1.slt
├── module2.slt
```

modules can be included inside of a source file using the `import` directive:

```
# module1.slt

from .              import module2;
from .other_modules import module3 as MODULE3;

alias VAR2 = module2.var2;

MODULE3.print_sum(module2.var1, VAR2);

let sum = MODULE3.add(1, 2); # [ERROR] MODULE3 does not export the 'add'
```

```
# module2.slt

@export let var1 : i64 = 123;
@export let var2 : i64 = 456;
```

```
# module3.slt

from std import io;

func add : const (a: i64, b: i64) -> i64 = a + b;

@export
func print_sum : const (a: i64, b: i64) -> unit = {
    io.print(add(a, b));
};
```