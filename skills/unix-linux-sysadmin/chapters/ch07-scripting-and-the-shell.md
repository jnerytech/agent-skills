# Chapter 7: Scripting and the Shell

## Core Idea
Scalable administration means changes are **structured, reproducible, and software-mediated** — not done by hand from memory. Master a shell (bash), an editor (vim), and a scripting language (Python) deeply. Use `sh` for gluing commands and light filters; graduate to Python/Ruby past ~50 lines or when you need real data structures and text processing.

## Frameworks Introduced
- **Write microscripts**: most efficiency comes from saving a few keystrokes everywhere, not from marquee 100-line scripts. Keep `~/bin` scriptlets, shell functions (in `.bash_profile`), and aliases. Ask of every chore: "how do I avoid doing this again?"
- **Develop scripts interactively as pipelines**: build a command pipeline one stage at a time at the prompt, sending to STDOUT and eyeballing it; nothing is done until output looks right (so nothing to undo); then execute for real, and capture with `fc` into a saved script.
- **Pick the right language**: `sh` (portable glue, always present), Python (the default general-purpose choice — well-designed, widely supported), Ruby (equivalent, web-associated, powers Chef/Puppet DSLs). Avoid Perl for new work; avoid csh/tcsh for scripting; avoid PHP/JS for sysadmin.
- **Scripting best practices**: usage message on bad args, validate inputs (sanity-check a path before `rm -rf`), meaningful exit codes (0 success), comment block header, errors to STDERR with program name, never make scripts setuid (use sudo).

## Key Concepts
- **File descriptors**: STDIN=0, STDOUT=1, STDERR=2. Unified I/O — channels can be terminal, file, pipe, socket.
- **Redirection**: `<` input from file; `>` overwrite STDOUT; `>>` append; `2>` STDERR; `>&`/`&>` both; `2>/dev/null` discard errors.
- **Pipe `|`** connects STDOUT→STDIN; `&&` run next only on success (exit 0); `||` run next only on failure; `;` sequence.
- **Quoting**: single quotes = literal; double quotes = globbing + `$var` expansion; backticks `` ` `` (or `$()`) = command substitution. `${var}` braces disambiguate.
- **Environment variables**: all-caps by convention; `export` promotes a shell var; child gets a *snapshot* (no live link). Set login-time vars in `~/.bash_profile`.
- **Regular expressions**: standard text-matching language used by grep/sed/Python `re`/Ruby. `.` any char, `*`/`+`/`?` quantifiers, `{n,m}` counts, `[...]` class, `^`/`$` anchors, `()` capture groups, `\1` backreference. Greedy by default.
- **Shebang `#!/bin/sh`** (or `#!/usr/bin/env ruby` to search PATH); execute bit makes a file runnable (UNIX ignores extensions).

## Mental Models
- **The prompt is an interactive script IDE.** Iterate a pipeline, preview with `echo`/`tee`, then pipe to `sh -x` to run for real — far less error-prone than editing in a text editor first.
- **`sh -x` (echo commands) / `sh -n` (syntax check, no run)** are your bash debuggers.
- **Filters chain like building blocks**: any command reading STDIN→STDOUT (`cut`, `sort`, `uniq`, `grep`, `wc`, `head`/`tail`, `tee`, `sed`) composes into pipelines.
- **Python: indentation IS the block structure** (no braces); colons introduce indented blocks; never mix tabs and spaces (4 spaces preferred).
- **Ruby: everything is an object and an expression; blocks (`do…end` / `{…}`) are first-class** — iteration is `collection.each do |x| … end`, not a language loop.

## Anti-patterns
- **Editing command lines with arrow keys**: learn emacs (`^A`/`^E`/`^R`) or `set -o vi` history editing.
- **Assuming `sh` == `bash`**: Ubuntu's `/bin/sh` is dash; bashisms break portable scripts (see wiki.ubuntu.com/DashAsBinSh). Limit to POSIX sh or require a specific interpreter deliberately.
- **`.` in `$PATH`**: lets others plant trap commands; always run local scripts as `./script`.
- **Premature optimization**: admin scripts should favor clarity over speed — 0.5s vs 2s rarely matters.
- **Not handling spaces/punctuation in filenames**: scripts must quote `"$var"` and cope with spaces, apostrophes, asterisks.
- **`copy, paste, and pray`**: don't script what you don't understand — scripts are read as authoritative docs.

## Code Examples
```sh
# Redirection & pipes
find / -name core 2>/dev/null > /tmp/corefiles   # matches to file, errors discarded
ps -ef | grep httpd
cut -d: -f7 /etc/passwd | sort | uniq -c          # count users per login shell
du -sh /usr/* | sort -h                           # human-numeric sort (2MB, 1.7G)
tail -f /var/log/messages | grep --line-buffered ZFS   # live-monitor + filter
find / -name core | tee /dev/tty | wc -l          # tap the stream: list AND count
sort -t: -k3,3 -n /etc/group                      # sort by 3rd colon field, numeric

# Shell function & alias
function backup () { mv "$1" "$1.$(date +%Y-%m-%d.%H%M.bak)"; }
alias ls='ls -Fh'

# sh script with input
#!/bin/sh
echo -n "Enter your name: "
read user_name
if [ -n "$user_name" ]; then echo "Hello $user_name!"; exit 0
else echo "Greetings, nameless one!"; exit 1; fi
```
```python
# Python: input validation idiom
import sys, os
def show_usage(msg, code=1):
    print(msg); print("%s: source dest" % sys.argv[0]); sys.exit(code)
if len(sys.argv) != 3: show_usage("2 args required")
elif not os.path.isdir(sys.argv[1]): show_usage("Invalid source")
source, dest = sys.argv[1:3]          # slice excludes far endpoint
import re
pat = re.compile("(%s)" % sys.argv[1])
pat.sub(r"_\1_", text)                # r"" = raw string for backreferences
```
```ruby
# Ruby: blocks + method chaining
elements.values.sort!.map(&:upcase).join(', ')
open('/etc/passwd','r') do |file|     # block auto-closes file on exit
  file.each_line { |line| print line if line.start_with? 'root:' }
end
"Hermann Hesse" =~ /H[aeiou]/         # => 0 (match index) or nil
ruby -F: -ane 'print $F[0], ":", $F[-1]' /etc/passwd   # one-liner filter
```

## Reference Tables
**Filter commands**: `cut` (fields, `-d` delim `-f` fields) · `sort` (`-n` numeric, `-h` human, `-t`/`-k` key, `-u` unique, `-r` reverse) · `uniq` (`-c` count, `-d` dups; needs presorted) · `wc` (`-l`/`-w`/`-c`) · `tee` (tap to file) · `head`/`tail` (`-n`, `tail -f` follow) · `grep` (`-i` ignore-case, `-v` invert, `-c` count, `-l` filenames, `-P` Perl regex).

**Language packaging**: Python → `pip install` / `pip search` (`--user` for home dir); Ruby → `gem install` / `gem search` (`--user-install`). Both resolve deps; only one version installed at a time in the basic environment (see Ch7's RVM/virtualenv for multi-version).

## Worked Example
**Rename `*.log` → `*.LOG` across a tree, safely.** Build it interactively: (1) `find . -name '*log'` — oops, matches `leather_flog` and directories; (2) refine to `find . -type f -name '*.log'`; (3) exclude a dangerous dir: `... | grep -v .do-not-touch`; (4) *preview* the commands without running them — `... | while read fname; do echo mv $fname $(echo $fname | sed s/.log/.LOG/); done` prints `mv foo.log foo.LOG …`; (5) once the preview is correct, pipe to `sh -x` to execute. Nothing destructive happened until step 5, and `sh -x` echoes each real command. Finally `fc` pulls the one-liner into your editor → add shebang + usage → save to `~/bin`.

## Key Takeaways
1. Automate relentlessly at every scale — scriptlets, shell functions, aliases — not just big set-piece scripts.
2. Learn one shell, one editor, one language deeply; they're "made of meat" (most features pay off).
3. Master pipes/redirection and the core filters; compose pipelines interactively and preview before executing.
4. Use `sh` for glue ≤50 lines; move to Python (default) or Ruby for real logic and data structures.
5. Write defensively: usage messages, input validation, exit codes, STDERR for errors, quote `"$var"`, never setuid scripts, never `.` in PATH.
6. Regular expressions are the universal pattern language across grep/sed/Python/Ruby — learn them once.

## Connects To
- **Ch 2**: shebang/execute bit; startup scripts.
- **Ch 6**: pip/gem packaging parallels OS package management.
- **Ch 23**: configuration management — the structured, scaled successor to scripting (and Ruby DSLs power Chef/Puppet).
- **Ch 4**: cron runs scripts on schedule (mind the non-login-shell environment).
