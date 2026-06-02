# Patterns from Git

Git's data model is built on copy-on-write immutable objects and efficient diffing.

| Pattern | Where | What It Does |
|---------|-------|--------------|
| [Copy-on-Write](/patterns/copy-on-write/) | `object-file.c` | Content-addressed immutable objects; branches share data, copy only on change |
| [Diff / Patch](/patterns/diff-patch/) | `diff.c`, `xdiff/` | Myers' diff algorithm for minimal edit distance between file versions |

## Further Reading

- [Git Source Code (GitHub)](https://github.com/git/git)
