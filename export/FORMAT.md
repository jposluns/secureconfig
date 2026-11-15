# Export list formats

The export publishes a chosen set of this repository's files as a separate public repository. These lists decide what it publishes and what it must never let through. `tools/export_lists.py` parses every one of them, and its `--check` mode holds the files in this folder to the checkout.

## Rules every list follows

- UTF-8 with LF line endings, no byte order mark, no carriage return, and no control or format character other than the tab that separates fields.
- The last line ends in LF.
- A line that is empty or starts with `#` is a comment. A line of whitespace alone is refused.
- Fields are separated by one tab, and a field never holds a tab.
- A path is relative to the repository root. It holds only ASCII letters, digits and the characters `.`, `_`, `+`, `@` and `-`, and never a `.` or `..` segment, an empty segment or a `.git` segment. Matching is case sensitive.

## The files in this folder

### public-allowlist.txt

Every path the export may publish, and nothing else. It is published, so it names public paths only. Each line is `KIND<TAB>PATH<TAB>NEED`, and a render line may add `<TAB>SOURCE`.

- KIND is `copy` (published byte for byte as it is in the input) or `render` (generated during the export).
- PATH is an exact path or a narrow glob: one `*` in the last segment, under a fixed directory, ending in a fixed suffix that holds a dot and a file type, such as `*.md`. A `*` matches one or more characters other than `/`, and never a name that starts with a dot. A glob at the repository root is refused, so each root file is named exactly.
- NEED is `required` (the export refuses when the file is missing) or `optional` (the file may be absent from the input).
- SOURCE, on a render line with an exact PATH, is the exact input path the file is rendered from.

### private-paths.txt

Every tracked path that stays private. It is never published. Each line is `deny<TAB>PATTERN`. A PATTERN is an exact path or a glob in which `**` stands for any number of whole segments (at least one when it ends the pattern) and each other segment holds at most one `*`.

### public-markers.txt

Generic shapes of citations of the project's working records. It is published. Each line is `ID<TAB>REGEX`: ID is lowercase ASCII letters and digits in words joined by single hyphens, unique in the file, and REGEX is a Python regular expression that compiles and does not match the empty string.

### public-exceptions.tsv

Exact lines of published files where a publishable marker is allowed. It is published. Each line is `PATH<TAB>LINE<TAB>SHA256<TAB>REF<TAB>REASON`:

- PATH is an exact path that a copy line publishes. An exception for a rendered file belongs on the rendered file and is checked on the staged tree.
- LINE is the line number, counted from 1, written without leading zeros.
- SHA256 is the SHA-256 of that line's bytes without its LF, in lowercase hexadecimal.
- REF is `marker:ID` for an ID in `public-markers.txt`.
- REASON says why the line may keep the hit. It is not empty and has no leading or trailing whitespace.

The same PATH, LINE and REF appear once. A row whose line is gone, has another SHA-256, or no longer holds a hit of what REF names fails the check.

## The private lists

The private lists are never committed. They are kept in a private directory outside every checkout, and the tool reads them from the directory given with `--private-dir`, or its default when none is given. The tool never creates, writes or lists that directory, and never prints what a list holds: a finding names the list, the line number and the rule broken, and a pass prints counts and each list's SHA-256.

`--check-private` refuses the directory unless it is an absolute path that is not a symbolic link, lies outside the repository, is owned by the user running the tool and is not group or world writable. Each list must be a regular file with mode 0600 owned by the same user.

### protected-terms.txt

One literal term per line, matched without regard to case at word boundaries. A term has no tab and no leading or trailing whitespace, and no two terms are equal ignoring case. The list holds at least one term.

### private-markers.txt

The same format as `public-markers.txt`, for shapes that would disclose something if published. It may hold no markers.

### exceptions.tsv

The same format as `public-exceptions.tsv`. REF is `marker:ID` for an ID in `private-markers.txt`, or `term:TERM` for a term in `protected-terms.txt`. A row that names a copied file is checked against the checkout; a row that names a rendered file is checked on the staged tree.
