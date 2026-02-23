from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def must_ok(p: subprocess.CompletedProcess, what: str) -> None:
    if p.returncode != 0:
        raise SystemExit(
            f"\n[ERROR] {what}\n"
            f"CMD: {' '.join(p.args)}\n"
            f"STDOUT:\n{p.stdout}\n"
            f"STDERR:\n{p.stderr}\n"
        )


def main() -> None:
    # 1) Validar que estás en repo git
    p = run(["git", "rev-parse", "--show-toplevel"])
    must_ok(p, "No estoy dentro de un repositorio git. Muévete a la carpeta del repo y reintenta.")
    root = Path(p.stdout.strip())

    # 2) Validar archivo de evidencia
    evidence = root / "results" / "unittest_run.txt"
    if not evidence.exists():
        raise SystemExit(
            "\n[ERROR] No existe results/unittest_run.txt\n"
            "Genera el archivo y vuelve a correr este script.\n"
        )

    content = evidence.read_text(encoding="utf-8", errors="ignore").lower()
    if "ok" not in content:
        print("[WARN] No detecté 'OK' dentro del archivo. Si tu corrida fue exitosa, puedes ignorar este warning.")

    # 3) Stage del archivo
    p_add = run(["git", "add", str(evidence.relative_to(root))])
    must_ok(p_add, "Falló git add para results/unittest_run.txt")

    # 4) Commit
    msg = "chore: add unittest run evidence"
    p_commit = run(["git", "commit", "-m", msg])

    # Si no hay cambios, git responde "nothing to commit"
    joined = (p_commit.stdout + p_commit.stderr).lower()
    if p_commit.returncode != 0 and "nothing to commit" in joined:
        print("[OK] No había cambios nuevos en unittest_run.txt (nothing to commit).")
    else:
        must_ok(p_commit, "Falló git commit")
        print("[OK] Commit creado:")
        print(p_commit.stdout.strip())

    # 5) Mostrar log corto
    p_log = run(["git", "log", "--oneline", "--decorate", "-n", "5"])
    must_ok(p_log, "No pude leer git log")
    print("\nÚltimos commits:\n" + p_log.stdout)


if __name__ == "__main__":
    main()