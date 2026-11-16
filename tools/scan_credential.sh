#!/usr/bin/env bash
# Literal credential search; invoke from the target repository root.
# Trust the launching shell, Bash/Git and Git configuration. BASH_ENV runs
# before this file: refusal here cannot undo a hostile startup file.
if [[ ${BASH_SOURCE[0]} != "$0" ]]; then
    builtin printf '%s\n' 'REFUSED: unsafe or wrong use; no content searched'
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
# Status 2 refuses unsafe or wrong use, always before any content search.
# Status 1 reports a match and outranks a failed search: once any search has
# matched, the scan ends FOUND, followed by an INCOMPLETE line if any search
# failed. Status 3 reports a scan that could not complete and matched nothing.
scan_refuse() {
    builtin printf '%s\n' 'REFUSED: unsafe or wrong use; no content searched'
    if (( explain )); then
        builtin printf 'CHECK: %s\n' "$1"
    fi
    exit 2
}
scan_fail() {
    builtin printf '%s\n' 'INCONCLUSIVE: could not complete scan'
    if (( explain )); then
        builtin printf 'CHECK: %s\n' "$1"
    fi
    exit 3
}
usage() {
    builtin printf '%s\n' \
        'Usage: bash tools/scan_credential.sh [--explain] OUTPUT_DIRECTORY' \
        'Run from the project repository root with a relative output directory.' \
        'Enter one key on stdin (silent on a terminal), never in argv or environment.' \
        'Exit: 0 NOT FOUND in stated scope; 1 FOUND, even if a search failed; 2 REFUSED; 3 INCONCLUSIVE.' \
        '--explain takes no key: check prerequisites and report the first refusal or failure.'
}
if [[ ${1-} == --help && $# == 1 ]]; then
    usage
    exit 0
fi
if [[ ${1-} == --explain ]]; then
    explain=1
    shift
fi
[[ $# == 1 ]] || scan_refuse arguments
[[ ! ${BASH_ENV+x} ]] || scan_refuse BASH_ENV
[[ $(builtin type -t printf) == builtin && $(builtin type -t read) == builtin &&
   $(builtin type -t compgen) == builtin && $(builtin type -t git) == file ]] ||
    scan_refuse command-resolution
(( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 3) )) ||
    scan_refuse bash-version

# Environment values inherit export, but not readonly/nameref/integer attributes.
# Source execution and BASH_ENV are refused, so plain unset suffices.
builtin unset -v key IFS GLOBIGNORE
IFS=$' \t\n'
builtin shopt -s globstar dotglob nullglob || scan_refuse glob-options
variables=$(compgen -v) || scan_refuse variable-list
for variable in $variables; do
    if [[ $variable == GIT_* ]]; then
        builtin unset -v "$variable" 2>/dev/null || scan_refuse git-environment
    fi
done
builtin trap 'scan_fail interrupted' HUP INT TERM

# Inspect ancestors too: trailing slashes must not hide symlinks or .git.
out=$1
[[ -n $out && $out != /* ]] || scan_refuse output-path
prefix=.
rest=$out
while [[ -n $rest ]]; do
    component=${rest%%/*}
    if [[ $rest == */* ]]; then
        rest=${rest#*/}
    else
        rest=
    fi
    [[ $component != .. && $component != .[gG][iI][tT] ]] || scan_refuse output-path
    [[ -n $component && $component != . ]] || continue
    prefix+=/$component
    [[ -d $prefix && ! -L $prefix && -r $prefix && -x $prefix ]] || scan_refuse output-root
done
out=$prefix
[[ -d $out && ! -L $out && -r $out && -x $out ]] || scan_refuse output-root
files=0
for entry in "$out"/**; do
    [[ $entry != */.[gG][iI][tT] && $entry != */.[gG][iI][tT]/* ]] || scan_refuse git-component
    [[ ! -L $entry && -r $entry && ( -f $entry || ( -d $entry && -x $entry ) ) ]] ||
        scan_refuse output-entry
    if [[ -f $entry ]]; then
        files=1
    fi
done
(( files )) || scan_refuse empty-output

# Only a presence marker crosses command substitution. read -d '' detects NUL
# and ordinary bytes, avoiding trailing-newline loss and Bash's NUL warning.
# FD 3 carries Git stdout; capture both pipeline statuses before any command.
# Return Git's 0 or 1 when it printed no diagnostic, 3 when it exited 0 or 1
# but printed one, and 2 otherwise.
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
        D:0:0 | D:1:0) return 3 ;;
        *) return 2 ;;
    esac
}
# A diagnostic from a rev-parse that exited 0 or 1 is a failed check. Any
# other failing rev-parse is wrong use, refused with 2, and so is a nonempty
# prefix (a subdirectory). Git's exit status cannot tell "not a repository"
# from a broken repository, so a broken repository is also refused with 2.
root_prefix=$(scan_git rev-parse --show-prefix 3>&1)
rc=$?
(( rc != 3 )) || scan_fail repository-root
[[ $rc == 0 && -z $root_prefix ]] || scan_refuse repository-root
commits=$(scan_git rev-list --all --reflog 3>&1)
rc=$?
[[ $rc == 0 ]] || scan_fail history-enumeration
if (( explain )); then
    printf '%s\n' 'READY: prerequisites passed; no key read and no content searched'
    exit 0
fi
IFS= read -rs key || scan_fail key-input
[[ -n $key && $key != *[[:cntrl:]]* ]] || scan_refuse key-input
# A search matched only when scan_git returned 0. A failed search does not stop
# the scan: every search still runs, so a match before or after it still counts.
# failed keeps the first failed search's category for scan_fail.
hit=0
failed=
scan_git grep --no-index -F -a -l -f - -- "$out"
rc=$?
if (( rc == 0 )); then
    hit=1
elif (( rc > 1 )); then
    failed=output-search
fi
while IFS= read -r commit; do
    [[ -n $commit ]] || continue
    scan_git grep -F -a -l -f - "$commit" --
    rc=$?
    if (( rc == 0 )); then
        hit=1
    elif (( rc > 1 )) && [[ -z $failed ]]; then
        failed=history-search
    fi
done <<< "$commits"
builtin unset -v key
if (( hit )); then
    printf '%s\n' 'FOUND: remove and rotate credential'
    if [[ -n $failed ]]; then
        printf '%s\n' 'INCOMPLETE: a search failed; the result above covers only what was searched'
    fi
    exit 1
fi
[[ -z $failed ]] || scan_fail "$failed"
printf '%s\n' 'NOT FOUND: no literal credential in stated scope'
exit 0
