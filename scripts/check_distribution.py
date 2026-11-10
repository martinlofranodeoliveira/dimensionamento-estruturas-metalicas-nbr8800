#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica a integridade dos artefatos construídos na pasta dist/ (sdist e wheel)."""

from __future__ import annotations

from pathlib import Path
import sys
import tarfile
import zipfile


def verificar_distribuicao() -> int:
    dist_dir = Path(__file__).parent.parent / "dist"
    if not dist_dir.exists():
        print("Erro: Diretório dist/ não encontrado. Execute 'python -m build' primeiro.", file=sys.stderr)
        return 1

    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))

    if not wheels or not sdists:
        print("Erro: Artefatos incompletos em dist/. Necessário pelo menos um .whl e um .tar.gz", file=sys.stderr)
        return 1

    wheel_path = wheels[0]
    sdist_path = sdists[0]

    print(f"Inspecionando Wheel: {wheel_path.name}")
    with zipfile.ZipFile(wheel_path) as zf:
        nomes = zf.namelist()
        print(f"  Total de membros no wheel: {len(nomes)}")
        assert any("py.typed" in n for n in nomes), "py.typed ausente no wheel"
        assert any("calculator.py" in n for n in nomes), "calculator.py ausente no wheel"
        assert any("cli.py" in n for n in nomes), "cli.py ausente no wheel"

    print(f"Inspecionando sdist: {sdist_path.name}")
    with tarfile.open(sdist_path, "r:gz") as tf:
        nomes_sdist = tf.getnames()
        print(f"  Total de membros no sdist: {len(nomes_sdist)}")
        assert any("pyproject.toml" in n for n in nomes_sdist), "pyproject.toml ausente no sdist"
        assert any("LICENSE" in n for n in nomes_sdist), "LICENSE ausente no sdist"

    print("✓ Distribuição inspecionada e aprovada com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(verificar_distribuicao())
