"""Signal parsing and operations for discrete-time signals.

This module defines a sparse integer-indexed `Signal` with utilities to parse
from the required TXT format and perform add, subtract, multiply, shift, and
fold operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Signal:
    """Discrete-time signal represented by a mapping from integer index to value.

    We store sparse samples keyed by index. For plotting and operations, indices
    are maintained as integers and values as floats.
    """

    samples: Dict[int, float]
    name: str | None = None

    @staticmethod
    def from_txt_lines(lines: List[str], name: str | None = None) -> "Signal":
        """Create a Signal from text lines in the specified format.

        Format:
        - line 1: N (number of samples)
        - next N lines: "index value"
        """
        if not lines:
            raise ValueError("Empty content")

        # Some test files include two leading zero lines before N.
        # We support both formats:
        #   1) [N, idx val, ...]
        #   2) [0, 0, N, idx val, ...]
        cursor = 0
        if len(lines) >= 3 and lines[0].strip() == "0" and lines[1].strip() == "0":
            cursor = 2
        try:
            n = int(lines[cursor].strip())
        except (TypeError, ValueError) as exc:
            raise ValueError("Header must contain integer N") from exc

        samples: Dict[int, float] = {}
        # Ensure we have at least N sample lines after the N header
        if len(lines) - (cursor + 1) < n:
            raise ValueError("Insufficient lines for provided N")

        for i in range(n):
            row = lines[cursor + 1 + i].strip()
            if not row:
                raise ValueError(f"Missing row for sample {i+1}")
            parts = row.split()
            if len(parts) != 2:
                raise ValueError(
                    f"Line {i+2} must have exactly two entries: index value"
                )
            try:
                idx = int(float(parts[0]))
                val = float(parts[1])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid index/value on line {i+2}") from exc
            samples[idx] = val

        return Signal(samples=samples, name=name)

    @staticmethod
    def from_txt_file(path: str, name: str | None = None) -> "Signal":
        """Read a TXT file and parse a `Signal`."""
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
        if name is None:
            name = path
        return Signal.from_txt_lines(lines, name=name)

    def to_sorted_series(self) -> Tuple[List[int], List[float]]:
        """Return sorted indices and corresponding values for plotting."""
        if not self.samples:
            return [], []
        xs = sorted(self.samples.keys())
        ys = [self.samples[i] for i in xs]
        return xs, ys

    def clone(self, name: str | None = None) -> "Signal":
        """Return a shallow copy, optionally with a new name."""
        return Signal(samples=dict(self.samples), name=name or self.name)

    # Operations
    def add(self, other: "Signal", name: str | None = None) -> "Signal":
        """Pointwise addition (missing indices treated as 0)."""
        result: Dict[int, float] = dict(self.samples)
        for idx, val in other.samples.items():
            result[idx] = result.get(idx, 0.0) + val
        return Signal(result, name=name)

    def subtract(self, other: "Signal", name: str | None = None) -> "Signal":
        """Pointwise subtraction (self - other)."""
        result: Dict[int, float] = dict(self.samples)
        for idx, val in other.samples.items():
            result[idx] = result.get(idx, 0.0) - val
        return Signal(result, name=name)

    def multiply(self, scalar: float, name: str | None = None) -> "Signal":
        """Scale signal by a scalar multiplier."""
        return Signal({i: v * scalar for i, v in self.samples.items()}, name=name)

    def shift(self, k: int, name: str | None = None) -> "Signal":
        """Shift indices by k: x(n-k). Positive k delays; negative k advances."""
        return Signal({i + k: v for i, v in self.samples.items()}, name=name)

    def fold(self, name: str | None = None) -> "Signal":
        """Time reversal: x(-n)."""
        return Signal({-i: v for i, v in self.samples.items()}, name=name)

