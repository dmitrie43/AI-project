"""
Фаза F: градиентный спуск на игрушке loss = (w - 3)^2

Запуск из C:\\Docker\\ai:
  python math-phase-f-gradient-demo.py

Цель: увидеть глазами, как lr влияет на спуск к w=3.
"""

from __future__ import annotations


def loss(w: float) -> float:
    """Штраф: чем дальше w от 3, тем больше."""
    return (w - 3.0) ** 2


def gradient(w: float) -> float:
    """
    Склон чаши в точке w.
    + значит «вгору направо» → чтобы вниз, уменьшаем w.
    """
    return 2.0 * (w - 3.0)


def run_descent(*, start: float, lr: float, steps: int) -> None:
    w = start
    print(f"\n=== start w={start}, lr={lr}, steps={steps} ===")
    print(f"{'step':>4}  {'w':>8}  {'loss':>8}  {'grad':>8}")
    for step in range(steps):
        g = gradient(w)
        print(f"{step:4d}  {w:8.3f}  {loss(w):8.3f}  {g:8.3f}")
        w = w - lr * g
    print(f"итог: w={w:.3f}, loss={loss(w):.3f}")


def main() -> None:
    print("Идеал: w=3, loss=0")
    print("Правило: w = w - lr * gradient")

    # 1) нормальный шаг — уверенно к 3
    run_descent(start=-2.0, lr=0.1, steps=25)

    # 2) слишком маленький — почти топчемся
    run_descent(start=-2.0, lr=0.01, steps=25)

    # 3) слишком большой — перескакиваем / скачем
    run_descent(start=-2.0, lr=1.5, steps=15)

    print("\nSummary:")
    print("- lr=0.1  : w moves toward 3, loss falls")
    print("- lr=0.01 : after 25 steps still far from 3")
    print("- lr=1.5  : loss explodes, overshoots minimum")


if __name__ == "__main__":
    main()
