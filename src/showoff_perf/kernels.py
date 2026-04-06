from __future__ import annotations


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def sum_primes_in_range(start: int, stop: int) -> int:
    total = 0
    for number in range(start, stop):
        if is_prime(number):
            total += number
    return total
