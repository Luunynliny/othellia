import numpy as np

from genetic.mutate import scramble, swap


def test_swap(monkeypatch):
    values = np.array([[1, 5], [2, 3], [4, 0]])
    i = 0

    class Mock_default_rng:
        def choice(self, a, size, replace):
            nonlocal i
            i += 1
            return values[i - 1]

    monkeypatch.setattr(np.random, "default_rng", Mock_default_rng)

    chromosome = np.array([1, 2, 3, 4, 5, 6])

    assert np.array_equal(swap(chromosome), np.array([1, 6, 3, 4, 5, 2]))
    assert np.array_equal(swap(chromosome), np.array([1, 2, 4, 3, 5, 6]))
    assert np.array_equal(swap(chromosome), np.array([5, 2, 3, 4, 1, 6]))


def test_scramble(monkeypatch):
    values = np.array([[1, 5], [2, 3], [0, 4]])
    i = 0

    class Mock_default_rng:
        def choice(self, a, size, replace):
            nonlocal i
            i += 1
            return values[i - 1]

        def shuffle(self, a):
            return a[::-1]

    monkeypatch.setattr(np.random, "default_rng", Mock_default_rng)

    chromosome = np.array([1, 2, 3, 4, 5, 6])

    assert np.array_equal(scramble(chromosome), np.array([1, 6, 5, 4, 3, 2]))
    assert np.array_equal(scramble(chromosome), np.array([1, 2, 4, 3, 5, 6]))
    assert np.array_equal(scramble(chromosome), np.array([5, 4, 3, 2, 1, 6]))
