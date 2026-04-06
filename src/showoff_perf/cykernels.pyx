# cython: language_level=3

cdef bint _is_prime(long long number):
    cdef long long divisor
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


cpdef long long sum_primes_in_range(long long start, long long stop):
    cdef long long total = 0
    cdef long long number
    for number in range(start, stop):
        if _is_prime(number):
            total += number
    return total
