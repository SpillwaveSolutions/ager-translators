from __future__ import annotations

import argparse
from pathlib import Path

from .emit import EMITTERS, TARGETS
from .ir import load_bundle


def compile_graph(target: str, bundle: Path | None, out: Path) -> list[Path]:
    if target not in EMITTERS:
        raise SystemExit(f"unknown target {target!r}; choose from {TARGETS}")
    graph = load_bundle(bundle)
    files = EMITTERS[target](graph)
    written: list[Path] = []
    for rel, content in files.items():
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written.append(dest)
    return written


def main() -> None:
    p = argparse.ArgumentParser(prog="ager-compile")
    p.add_argument("--list", action="store_true")
    p.add_argument("--target", choices=TARGETS)
    p.add_argument("--bundle", type=Path)
    p.add_argument("--out", type=Path, default=Path("generated"))
    args = p.parse_args()
    if args.list or not args.target:
        print("targets:", ", ".join(TARGETS))
        return
    written = compile_graph(args.target, args.bundle, args.out)
    print(f"wrote {len(written)} files to {args.out}")
    for w in written:
        print(" ", w)


if __name__ == "__main__":
    main()
