from __future__ import annotations

from showoff_perf.kernels import is_prime, sum_primes_in_range


def test_is_prime_handles_basic_numbers() -> None:
    assert is_prime(1) is False
    assert is_prime(2) is True
    assert is_prime(9) is False
    assert is_prime(13) is True


def test_sum_primes_in_range_returns_expected_total() -> None:
    assert sum_primes_in_range(2, 10) == 17
