# Export list formats

These lists describe a planned export that publishes a chosen set of this repository's files as a separate public repository: what it may publish, and what it must never let through. `tools/export_lists.py` parses every one of them, and its `--check` mode holds the files in this folder to the checkout.

## Rules every list follows

- UTF-8 with LF line endings, no byte order mark, no carriage return, and no control or format character other than the tab that separates fields.
- The last line ends in LF.
- A line that is empty or starts with `#` is a comment. A line of whitespace alone is refused.
- Fields are separated by single tabs, so a field never holds a tab: a line with more tabs than its format allows is refused.
- A path is relative to the repository root. It holds only ASCII letters, digits and the characters `.`, `_`, `+`, `@` and `-`, and never a `.` or `..` segment, an empty segment or a `.git` segment. Matching is case sensitive.

## The files in this folder

### public-allowlist.txt

Every path the export may publish, and nothing else. It lists itself, so it names public paths only. Each line is `KIND<TAB>PATH<TAB>NEED`, and a render line may add `<TAB>SOURCE`.

- KIND is `copy` (a file to be published byte for byte as it is in the input) or `render` (a file to be generated during the export).
- PATH is an exact path or a narrow glob: one `*` in the last segment, under a fixed directory, ending in a fixed suffix that holds a dot and a file type, such as `*.md`. A `*` matches one or more characters other than `/`, and never a name that starts with a dot. A glob at the repository root is refused, so each root file is named exactly.
- NEED is `required` (the line must match at least one tracked path) or `optional` (the line may match none, for a file that is not in the checkout yet).
- SOURCE, on a render line with an exact PATH, is the exact input path the file is rendered from.

`--check` fails a tracked path that a copy or render line matches unless it is a regular file, not a symbolic link or a submodule, and its name keeps to the path characters above. It also fails a copy or render line that can match any path a deny line matches, whether or not that path is tracked.

### private-paths.txt

Every tracked path that stays private. The allowlist does not list it. Each line is `deny<TAB>PATTERN`, and may add `<TAB>NEED` with the meaning above; a line without one is `required`. A PATTERN is an exact path or a glob in which `**` stands for any number of whole segments (at least one when it ends the pattern) and each other segment holds at most one `*`. A tracked path that stays private matches exactly one deny line.

Two deny patterns may overlap: the rule above holds for tracked paths only, so `--check` fails a tracked path that two deny lines match, not the two patterns themselves. The shipped `**/*-latest.zip` line overlaps the directory lines on purpose, so that `--check` refuses any copy or render line that can match a latest archive anywhere.

### public-markers.txt

Generic shapes of citations of the project's working records, and of links into its development history. The allowlist lists it, so it holds no shape that spells out what stays private, such as the names of the private paths; such a shape belongs in `private-markers.txt`. Each line is `ID<TAB>REGEX`: ID is lowercase ASCII letters and digits in words joined by single hyphens, unique in the file, and REGEX is a Python regular expression that compiles without a warning from the compiler and can never match an empty string, so a pattern that can match zero characters, such as `\b` or `(?=x)` alone, is refused. A compiler warning, such as the one for a possible nested set in `[[x]`, is a finding, and so is a pattern whose shortest match the tool cannot work out.

### public-exceptions.tsv

Exact lines of published files where a publishable marker is allowed. The allowlist lists it. Each line is `PATH<TAB>LINE<TAB>SHA256<TAB>REF<TAB>REASON`:

- PATH is an exact path that a copy line publishes. `--check` refuses a row that names a rendered file, since that file exists only once the export renders it.
- LINE is the line number, counted from 1, written without leading zeros.
- SHA256 is the SHA-256 of that line's bytes without its LF, in lowercase hexadecimal.
- REF is `marker:ID` for an ID in `public-markers.txt`.
- REASON says why the line may keep the hit. It is not empty and has no leading or trailing whitespace.

The same PATH, LINE and REF appear once. A row whose line is gone, has another SHA-256, or no longer holds a hit of what REF names fails the check.

## The private lists

The private lists are never committed. They are kept in a private directory outside every checkout. The tool reads them from the directory given with `--private-dir`, else from the one the `SECURECONFIG_EXPORT_PRIVATE` environment variable names, else from its built-in default. It never creates, writes or lists that directory, and never prints what a list holds or any part of the directory's path. A finding names the list and the rule broken, with the line number for a line, or the byte offset of the first byte that is not UTF-8, and never a message or warning of the regular expression compiler, which can quote or locate a pattern. A pass prints counts and each list's SHA-256. The tool accepts no abbreviated option, and when an argument starts with `--priv` or `--check-p`, a prefix of `--private-dir` or `--check-private`, a usage error prints the usage and a fixed message and repeats no argument, in either mode, so a misspelled private option does not echo the path after it.

`--check-private` opens the directory once, without following a symbolic link, and refuses it unless it is an absolute path that lies outside the repository, is owned by the user running the tool and is not group or world writable. It opens each list through that open directory, without following a symbolic link, and refuses it unless it is a regular file with mode 0600 owned by the same user. The directories above the private directory are not checked.

### protected-terms.txt

One literal term per line, matched without regard to case at word boundaries. A term has no tab and no leading or trailing whitespace, and no two terms are equal ignoring case. The list holds at least one term.

### private-markers.txt

The same format as `public-markers.txt`, for shapes that would disclose something if published, such as links into the paths that stay private, which spell out their names, and the naming of private repositories.

For each deny line of `private-paths.txt`, `--check-private` builds a path the line keeps private, with each `**` and `*` written as `x`, and two links to it: `https://github.com/example-org/secureconfig/blob/main/PATH` and `https://raw.githubusercontent.com/example-org/secureconfig/main/PATH`. It fails the deny line unless some private marker finds each link, so a list that passes holds at least one marker.

A link whose ref holds a `/`, such as a branch named `feature/x`, is not built: in such a link the ref cannot be told apart from a directory, so a marker that finds it would also find a link into a public file under a directory with a private name.

### exceptions.tsv

The same format as `public-exceptions.tsv`. REF is `marker:ID` for an ID in `private-markers.txt`, or `term:TERM` for a term in `protected-terms.txt`. A row that names a copied file is checked against the checkout; a row that names a rendered file is counted but not checked, since that file exists only once the export renders it.
