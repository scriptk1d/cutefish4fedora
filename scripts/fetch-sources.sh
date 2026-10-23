#!/usr/bin/env bash
# Downloads the source tarballs the specs pin into SOURCES/.
#
#   scripts/fetch-sources.sh                 # every spec
#   scripts/fetch-sources.sh cutefish-dm     # only these specs
#
# Every spec carries its commit in a "%global commit <sha>" line, which is the
# only place the pin lives. Skia is fetched separately: it is pinned in
# cutefish-toolkit.spec with %global skiarev and is not a GitHub tarball, so it
# is only fetched when the toolkit itself is requested.
set -Eeuo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
sources=${SOURCES:-$root/SOURCES}
skia_cache=${SKIA_CACHE:-$root/.cache/skia}
wanted=("$@")
mkdir -p "$sources"

fetch() {
    local url=$1 out=$2
    if [ -s "$out" ]; then
        echo "have $(basename "$out")"
        return
    fi
    echo "fetch $(basename "$out")"
    curl -fL --retry 3 --retry-delay 2 -o "$out.part" "$url"
    mv "$out.part" "$out"
}

for spec in "$root"/specs/*.spec; do
    repo=$(sed -n 's/^%global repo \([^[:space:]]*\)$/\1/p' "$spec" | head -n1)
    commit=$(sed -n 's/^%global commit \([0-9a-f]\{40\}\)$/\1/p' "$spec" | head -n1)
    name=$(basename "$spec" .spec)
    if [ -z "$repo" ] || [ -z "$commit" ]; then
        echo "cannot read repo/commit from $spec" >&2
        exit 1
    fi

    if [ ${#wanted[@]} -gt 0 ]; then
        skip=1
        for want in "${wanted[@]}"; do
            if [ "$want" = "$name" ] || [ "$want" = "$repo" ]; then
                skip=0
            fi
        done
        if [ "$skip" = 1 ]; then
            continue
        fi
    fi

    fetch "https://codeload.github.com/cutefishos/$repo/tar.gz/$commit" \
        "$sources/$repo-$commit.tar.gz"
done

fetch_skia=0
if [ ${#wanted[@]} -eq 0 ]; then
    fetch_skia=1
else
    for want in "${wanted[@]}"; do
        if [ "$want" = "cutefish-toolkit" ] || [ "$want" = "cutefish-toolkit-devel" ]; then
            fetch_skia=1
        fi
    done
fi
if [ "$fetch_skia" = 0 ]; then
    exit 0
fi

# Skia: same checkout scripts/fetch-skia.sh makes in the toolkit repository.
spec=$root/specs/cutefish-toolkit.spec
rev=$(sed -n 's/^%global skiarev \([0-9a-f]\{40\}\)$/\1/p' "$spec" | head -n1)
branch=$(sed -n 's/^%global skiabranch \([^[:space:]]*\)$/\1/p' "$spec" | head -n1)
out=$sources/skia-$rev.tar.gz

if [ -s "$out" ]; then
    echo "have $(basename "$out")"
    exit 0
fi

if [ -n "${SKIA_CHECKOUT:-}" ]; then
    src=$SKIA_CHECKOUT
elif [ -d "$skia_cache/.git" ]; then
    src=$skia_cache
else
    src=$skia_cache
    mkdir -p "$(dirname "$src")"
    echo "clone skia $branch"
    git clone --quiet --filter=blob:none --no-checkout --depth 1 \
        --branch "$branch" https://skia.googlesource.com/skia "$src"
fi

if [ -f "$src/BUILD.gn" ] && [ -x "$src/bin/gn" ] && \
   [ "$(git -C "$src" rev-parse HEAD 2>/dev/null || true)" = "$rev" ]; then
    echo "use skia checkout $(basename "$src")"
else
    echo "checkout skia $rev"
    git -C "$src" sparse-checkout set --cone bin build_overrides \
        experimental/ffmpeg gn include modules src third_party
    git -C "$src" fetch --quiet --filter=blob:none --depth 1 origin "$rev"
    git -C "$src" checkout --quiet --detach "$rev"
fi
[ -x "$src/bin/gn" ] || python3 "$src/bin/fetch-gn"

echo "pack $(basename "$out")"
tar --exclude=.git --transform "s,^\./,skia-$rev/," -czf "$out.part" -C "$src" .
mv "$out.part" "$out"
