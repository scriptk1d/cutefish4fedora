#!/usr/bin/env bash
# Moves every spec's pin to the tip of the upstream repository's main branch.
#
#   scripts/update-pins.sh                 # all specs
#   scripts/update-pins.sh terminal icons  # only these repositories
#   GITHUB_TOKEN=... scripts/update-pins.sh
#
# The Skia revision cutefish-toolkit builds against is read from the toolkit's
# own scripts/fetch-skia.sh at the pinned commit, so a toolkit bump cannot
# leave the spec building against a stale Skia.
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
wanted=("$@")

api() {
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" "$1"
    else
        curl -fsSL "$1"
    fi
}

for spec in "$root"/specs/*.spec; do
    name=$(basename "$spec" .spec)
    repo=$(sed -n 's/^%global repo \([^[:space:]]*\)$/\1/p' "$spec" | head -n1)
    old=$(sed -n 's/^%global commit \([0-9a-f]\{40\}\)$/\1/p' "$spec" | head -n1)

    if [ ${#wanted[@]} -gt 0 ]; then
        skip=1
        for want in "${wanted[@]}"; do
            [ "$want" = "$name" ] || [ "$want" = "$repo" ] && skip=0
        done
        [ "$skip" -eq 0 ] || continue
    fi

    sha=$(git ls-remote "https://github.com/cutefishos/$repo.git" refs/heads/main | cut -f1)
    [ -n "$sha" ] || { echo "$repo: no main branch" >&2; exit 1; }

    # Release numbers carry the commit date: 1970-01-01 -> 19700101.
    date=$(api "https://api.github.com/repos/cutefishos/$repo/commits/$sha" |
        grep -o '"date": "[0-9-]*' | head -n1 | cut -d'"' -f4 | tr -d '-')

    if [ "$sha" = "$old" ]; then
        echo "$repo: unchanged at $sha"
        continue
    fi

    sed -i \
        -e "s/^%global commit .*/%global commit $sha/" \
        -e "s/^%global shortcommit .*/%global shortcommit ${sha:0:7}/" \
        -e "s/^%global commitdate .*/%global commitdate $date/" \
        "$spec"
    rm -f "$root/SOURCES/$repo-"*.tar.gz

    echo "$repo: $old -> $sha ($date)"
done

sync_skia=0
if [ ${#wanted[@]} -eq 0 ]; then
    sync_skia=1
else
    for want in "${wanted[@]}"; do
        [ "$want" = "cutefish-toolkit" ] && sync_skia=1
    done
fi

if [ "$sync_skia" = "1" ]; then
    spec=$root/specs/cutefish-toolkit.spec
    commit=$(sed -n 's/^%global commit \([0-9a-f]\{40\}\)$/\1/p' "$spec" | head -n1)
    upstream=$(api "https://raw.githubusercontent.com/cutefishos/cutefish-toolkit/$commit/scripts/fetch-skia.sh")
    branch=$(printf '%s\n' "$upstream" | sed -n 's/^SKIA_BRANCH=//p' | head -n1)
    rev=$(printf '%s\n' "$upstream" | sed -n 's/^SKIA_REVISION=//p' | head -n1)
    [ -n "$branch" ] && [ -n "$rev" ] ||
        { echo "cannot read the Skia pin from fetch-skia.sh" >&2; exit 1; }

    oldbranch=$(sed -n 's/^%global skiabranch //p' "$spec" | head -n1)
    oldrev=$(sed -n 's/^%global skiarev //p' "$spec" | head -n1)
    if [ "$branch" = "$oldbranch" ] && [ "$rev" = "$oldrev" ]; then
        echo "skia: unchanged at $branch@$rev"
    else
        sed -i \
            -e "s|^%global skiabranch .*|%global skiabranch $branch|" \
            -e "s|^%global skiarev .*|%global skiarev $rev|" \
            "$spec"
        rm -f "$root/SOURCES/skia-"*.tar.gz
        echo "skia: $oldbranch@$oldrev -> $branch@$rev"
    fi
fi
