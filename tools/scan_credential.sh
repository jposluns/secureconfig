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
# Status 1 reports a match and outranks an incomplete scan: once any search has
# matched, the scan ends FOUND, followed by an INCOMPLETE line if any search
# failed or a signal cut the scan short. Status 3 means the result is not
# known: the scan could not complete before any search matched.
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
        'Exit: 0 NOT FOUND in stated scope; 1 FOUND, even if the scan was incomplete; 2 REFUSED; 3 INCONCLUSIVE, result not known.' \
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
# Set before the trap: inherited values must not reach the arithmetic below.
# Before the content searches a HUP, INT or TERM ends the scan with status 3
# once the running command returns; during them it only sets interrupted.
hit=0
failed=
interrupted=0
searching=0
scan_scope=
# Run only by the builtin trap below; a bare trap would admit an exported trap function.
# shellcheck disable=SC2329
scan_signal() {
    if (( searching )); then
        interrupted=1
    else
        scan_fail interrupted
    fi
}
builtin trap scan_signal HUP INT TERM

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

# Only markers and statuses cross command substitution, on FD 5: D when Git
# wrote to stderr (read -d '' detects NUL and ordinary bytes, avoiding
# trailing-newline loss and Bash's NUL warning), P when the key could not be
# written to Git in full, M after each verified name the scan printed, V for a
# line that names no real path in the search's scope, T for a last line cut
# short, and the G, R and F statuses of Git, the diagnostic reader and the
# name forwarder, each captured before any other command. FD 3 carries the
# scan's stdout. A search's names pass through scan_forward, which ignores
# HUP, INT and TERM, so those signals cannot stop it between printing a name
# and writing its M.
exec 3>&1
scan_run() {
    if [[ $1 == grep ]]; then
        printf '%s\n' "$key" | git --no-pager --literal-pathspecs "$@" 5>&-
        statuses=("${PIPESTATUS[@]}")
        if (( statuses[0] != 0 )); then
            printf P >&5
            return 2
        fi
        return "${statuses[1]}"
    fi
    git --no-pager --literal-pathspecs "$@" 5>&-
}
scan_diagnostic() {
    local diagnostic='' read_status
    IFS= read -r -d '' diagnostic
    read_status=$?
    if [[ -n $diagnostic ]] || (( read_status == 0 )); then
        printf D
    fi
}
scan_capture() {
    scan_run "$@" 2>&1 >&4 4>&- | scan_diagnostic >&5 4>&-
    statuses=("${PIPESTATUS[@]}")
    printf 'G%s.R%s.' "${statuses[0]}" "${statuses[1]}" >&5
}
# Decode one core.quotePath C-quoted name into REPLY, or fail on a malformed
# one. Git emits \a \b \f \n \r \t \v \\ \" and three-digit octal escapes.
scan_unquote() {
    local quoted=${1#\"} escape octal
    quoted=${quoted%\"}
    REPLY=
    while [[ -n $quoted ]]; do
        if [[ ${quoted:0:1} != \\ ]]; then
            REPLY+=${quoted:0:1}
            quoted=${quoted:1}
            continue
        fi
        escape=${quoted:1:1}
        case $escape in
            a) REPLY+=$'\a' ;;
            b) REPLY+=$'\b' ;;
            f) REPLY+=$'\f' ;;
            n) REPLY+=$'\n' ;;
            r) REPLY+=$'\r' ;;
            t) REPLY+=$'\t' ;;
            v) REPLY+=$'\v' ;;
            \\) REPLY+=\\ ;;
            '"') REPLY+='"' ;;
            [0-3])
                octal=${quoted:1:3}
                [[ $octal == [0-3][0-7][0-7] && $octal != 000 ]] || return 1
                printf -v escape '%b' "\\0$octal" || return 1
                REPLY+=$escape
                quoted=${quoted:2}
                ;;
            *) return 1 ;;
        esac
        quoted=${quoted:2}
    done
}
# A printed line counts, and reaches stdout, only when it names a real path in
# the search's scope: for the output search an existing non-symlink path under
# the output directory, and for a history search a path that exists in the
# searched commit itself (git cat-file -e on commit:path). Color escapes are
# stripped and a C-quoted name is decoded before the check; the line itself is
# forwarded unchanged, so a garbled, empty, partial or non-path line can never
# read as FOUND and never reaches stdout.
scan_verify() {
    local name=$1 color=$'\e\\[[0-9;]*m'
    while [[ $name =~ $color ]]; do
        name=${name//"${BASH_REMATCH[0]}"/}
    done
    if [[ $name == \"*\" ]]; then
        scan_unquote "$name" || return 1
        name=$REPLY
    fi
    [[ -n $name ]] || return 1
    if [[ -n $scan_scope ]]; then
        [[ $name == "$scan_scope":?* ]] || return 1
        git --no-pager --literal-pathspecs cat-file -e "$name" >/dev/null 2>&1 5>&-
    else
        [[ $name == "${out#./}"/?* && /$name/ != */../* && /$name/ != */./* ]] || return 1
        [[ -e ./$name && ! -L ./$name ]]
    fi
}
scan_forward() {
    local line
    builtin trap '' HUP INT TERM
    while IFS= read -r line; do
        if scan_verify "$line"; then
            printf '%s\n' "$line" >&3 || return 2
            printf M
        else
            printf V
        fi
    done
    if [[ -n $line ]]; then
        printf T
    fi
}
# Return Git's 0 or 1 when nothing failed, 3 when Git exited 0 or 1 but
# printed a diagnostic and nothing else failed, and 2 otherwise. With the
# whole key written to Git, a search sets git_matched to 1 when Git exited 0
# or the scan printed a verified name from it. A failed search sets
# git_failure to how it failed, in fixed wording.
scan_git() {
    local result status=none detector=none forward=0
    local status_pattern='G([0-9]+)[.]' detector_pattern='R([0-9]+)[.]'
    local forward_pattern='F([0-9]+)[.]'
    git_matched=0
    git_failure=
    if [[ $1 == grep ]]; then
        result=$(
            {
                scan_capture "$@" 4>&1 | scan_forward
                printf 'F%s.' "${PIPESTATUS[1]}"
            } 5>&1
        )
        forward=none
        if [[ $result =~ $forward_pattern ]]; then
            forward=${BASH_REMATCH[1]}
        fi
    else
        result=$(scan_capture "$@" 4>&3 5>&1)
    fi
    if [[ $result =~ $status_pattern ]]; then
        status=${BASH_REMATCH[1]}
    fi
    if [[ $result =~ $detector_pattern ]]; then
        detector=${BASH_REMATCH[1]}
    fi
    if [[ $result != *P* && ( $status == 0 || $result == *M* ) ]]; then
        git_matched=1
    fi
    if [[ $result == *P* ]]; then
        git_failure='could not pass the key to Git'
    elif [[ $result == *T* ]]; then
        git_failure='printed an unterminated last line'
    elif [[ $result == *V* ]]; then
        git_failure='printed a line that names no path in its scope'
    elif [[ $result == *D* ]]; then
        git_failure='printed a Git diagnostic'
    elif [[ $status == none || $forward == none ]]; then
        git_failure='stopped before its status was read'
    elif [[ $forward != 0 ]]; then
        git_failure='could not print its matching names'
    elif [[ $detector != 0 ]]; then
        git_failure='could not be checked for a Git diagnostic'
    elif [[ $status != [01] ]]; then
        git_failure='ended with a Git error status'
    else
        return "$status"
    fi
    if [[ $result == *D* && $result != *P* && $result != *[TV]* && $forward == 0 &&
          $detector == 0 && $status == [01] ]]; then
        return 3
    fi
    return 2
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
# A search matched when scan_git set git_matched, even if the search failed.
# A failed search does not stop the scan: every search still runs, so a match
# before or after it still counts. A HUP, INT or TERM during the searches
# ends the scan once the search in progress returns, and is reported only
# when it left a commit unsearched: a signal that leaves no search unrun does
# not make the scan incomplete. failed keeps the first failed search's
# wording for the INCOMPLETE line, naming the commit for a history search.
# With no match, a failed or cut-short scan ends INCONCLUSIVE without a CHECK
# line, since --explain exits before any search.
scan_search() {
    local search=$1
    scan_scope=$2
    shift 2
    scan_git grep "$@"
    rc=$?
    (( ! git_matched )) || hit=1
    if (( rc > 1 )) && [[ -z $failed ]]; then
        failed="$search $git_failure"
    fi
}
searching=1
scan_search 'the output search' '' --no-index -F -a -l -f - -- "$out"
cut_short=0
while IFS= read -r commit; do
    [[ -n $commit ]] || continue
    if (( interrupted )); then
        cut_short=1
        break
    fi
    scan_search "the history search of commit $commit" "$commit" -F -a -l -f - "$commit" --
done <<< "$commits"
builtin unset -v key
if (( cut_short )); then
    failed+="${failed:+, and }the scan was interrupted by a signal"
fi
if (( hit )); then
    printf '%s\n' 'FOUND: remove and rotate credential'
    if [[ -n $failed ]]; then
        printf 'INCOMPLETE: %s; the result above covers only what was searched\n' "$failed"
    fi
    exit 1
fi
[[ -z $failed ]] || scan_fail content-search
printf '%s\n' 'NOT FOUND: no literal credential in stated scope'
exit 0
