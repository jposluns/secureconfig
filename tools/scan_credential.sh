#!/usr/bin/env bash
# Literal credential search; invoke from the target repository root.
# Trust the launching shell, Bash/Git and Git configuration. BASH_ENV runs
# before this file: refusal here cannot undo a hostile startup file.
if [[ ${BASH_SOURCE[0]} != "$0" ]]; then
    builtin printf '%s\n' 'INCONCLUSIVE: could not complete scan'
    return 2
fi
builtin trap - DEBUG RETURN ERR EXIT
builtin set +x +a +e +u +f
builtin set +o posix
builtin shopt -u expand_aliases failglob

# Exported functions survive a new Bash. Other shell primitives must be trusted.
builtin unset -f printf read git
builtin enable printf read
explain=0
scan_fail() {
    builtin printf '%s\n' 'INCONCLUSIVE: could not complete scan'
    if (( explain )); then
        builtin printf 'CHECK: %s\n' "$1"
    fi
    exit 2
}
usage() {
    builtin printf '%s\n' \
        'Usage: bash tools/scan_credential.sh [--explain] OUTPUT_DIRECTORY' \
        'Run from the project repository root with a relative output directory.' \
        'Enter one key on stdin (silent on a terminal), never in argv or environment.' \
        'Exit: 0 NOT FOUND in stated scope; 1 FOUND; 2 INCONCLUSIVE.' \
        '--explain takes no key: check prerequisites and report the first refusal.'
}
if [[ ${1-} == --help && $# == 1 ]]; then
    usage
    exit 0
fi
if [[ ${1-} == --explain ]]; then
    explain=1
    shift
fi
[[ $# == 1 ]] || scan_fail arguments
[[ ! ${BASH_ENV+x} ]] || scan_fail BASH_ENV
[[ $(builtin type -t printf) == builtin && $(builtin type -t read) == builtin &&
   $(builtin type -t compgen) == builtin && $(builtin type -t git) == file ]] ||
    scan_fail command-resolution
(( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 3) )) ||
    scan_fail bash-version

# Environment values inherit export, but not readonly/nameref/integer attributes.
# Source execution and BASH_ENV are refused, so plain unset suffices.
builtin unset -v key IFS GLOBIGNORE
IFS=$' \t\n'
builtin shopt -s globstar dotglob nullglob || scan_fail glob-options
variables=$(compgen -v) || scan_fail variable-list
for variable in $variables; do
    if [[ $variable == GIT_* ]]; then
        builtin unset -v "$variable" 2>/dev/null || scan_fail git-environment
    fi
done
builtin trap 'scan_fail interrupted' HUP INT TERM

# Inspect ancestors too: trailing slashes must not hide symlinks or .git.
out=$1
[[ -n $out && $out != /* ]] || scan_fail output-path
prefix=.
rest=$out
while [[ -n $rest ]]; do
    component=${rest%%/*}
    if [[ $rest == */* ]]; then
        rest=${rest#*/}
    else
        rest=
    fi
    [[ $component != .. && $component != .[gG][iI][tT] ]] || scan_fail output-path
    [[ -n $component && $component != . ]] || continue
    prefix+=/$component
    [[ -d $prefix && ! -L $prefix && -r $prefix && -x $prefix ]] || scan_fail output-root
done
out=$prefix
[[ -d $out && ! -L $out && -r $out && -x $out ]] || scan_fail output-root
files=0
for entry in "$out"/**; do
    [[ $entry != */.[gG][iI][tT] && $entry != */.[gG][iI][tT]/* ]] || scan_fail git-component
    [[ ! -L $entry && -r $entry && ( -f $entry || ( -d $entry && -x $entry ) ) ]] ||
        scan_fail output-entry
    if [[ -f $entry ]]; then
        files=1
    fi
done
(( files )) || scan_fail empty-output

# Only a presence marker crosses command substitution. read -d '' detects NUL
# and ordinary bytes, avoiding trailing-newline loss and Bash's NUL warning.
# FD 3 carries Git stdout; capture both pipeline statuses before any command.
exec 3>&1
scan_git() {
    local result
    result=$(
        {
            if [[ $1 == grep ]]; then
                printf '%s\n' "$key" | git --no-pager --literal-pathspecs "$@"
                statuses=("${PIPESTATUS[@]}")
                (( statuses[0] == 0 )) || exit 2
                exit "${statuses[1]}"
            else
                git --no-pager --literal-pathspecs "$@"
            fi
        } 2>&1 >&3 | {
            diagnostic=
            IFS= read -r -d '' diagnostic
            read_status=$?
            if [[ -n $diagnostic ]] || (( read_status == 0 )); then
                printf D
            fi
        }
        statuses=("${PIPESTATUS[@]}")
        printf ':%s:%s' "${statuses[0]}" "${statuses[1]}"
    )
    case $result in
        :0:0) return 0 ;;
        :1:0) return 1 ;;
        *) return 2 ;;
    esac
}
root_prefix=$(scan_git rev-parse --show-prefix 3>&1)
rc=$?
[[ $rc == 0 && -z $root_prefix ]] || scan_fail repository-root
commits=$(scan_git rev-list --all --reflog 3>&1)
rc=$?
[[ $rc == 0 ]] || scan_fail history-enumeration
if (( explain )); then
    printf '%s\n' 'READY: prerequisites passed; no key read and no content searched'
    exit 0
fi
IFS= read -rs key || scan_fail key-input
[[ -n $key && $key != *[[:cntrl:]]* ]] || scan_fail key-input
hit=0
scan_git grep --no-index -F -a -l -f - -- "$out"
rc=$?
(( rc <= 1 )) || scan_fail output-search
if (( rc == 0 )); then
    hit=1
fi
while IFS= read -r commit; do
    [[ -n $commit ]] || continue
    scan_git grep -F -a -l -f - "$commit" --
    rc=$?
    (( rc <= 1 )) || scan_fail history-search
    if (( rc == 0 )); then
        hit=1
    fi
done <<< "$commits"
builtin unset -v key
if (( hit )); then
    printf '%s\n' 'FOUND: remove and rotate credential'
    exit 1
fi
printf '%s\n' 'NOT FOUND: no literal credential in stated scope'
exit 0
