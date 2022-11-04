from multiprocessing import shared_memory

import numpy as np

SHARED_MEMORY_NAME = "shared_noise_table"


class SharedNoiseTable:
    def __init__(self):
        import ctypes

        seed = 123
        count = 250000000  # 1 gigabyte of 32-bit numbers. Will actually sample 2 gigabytes below.

        self.rng = np.random.default_rng()
        self.noise = self.rng.standard_normal(size=count, dtype=np.float32)

        shm = shared_memory.SharedMemory(name=SHARED_MEMORY_NAME, create=True, size=self.noise.nbytes)

        b = np.array(self.noise.shape, dtype=self.noise.dtype, buffer=shm.buf)
        b[:] = self.noise[:]


        # logger.info('Sampling {} random numbers with seed {}'.format(count, seed))

        #self._shared_mem = multiprocessing.Array(ctypes.c_float, count)
        self.noise = np.ctypeslib.as_array(self._shared_mem.get_obj())

        assert self.noise.dtype == np.float32

        self.noise[:] = np.random.RandomState(seed).randn(count)  # 64-bit to 32-bit conversion here

        #logger.info('Sampled {} bytes'.format(self.noise.size * 4))

    def get(self, i: int, dim: int):
        return self.noise[i:i + dim]

    def sample_index(self, stream, dim):
        return stream.randint(0, len(self.noise) - dim + 1)


class Adam:
    def __init__(self, num_params, stepsize, beta1=0.9, beta2=0.999, epsilon=1e-08):
        self.dim = num_params
        self.t = 0

        self.stepsize = stepsize
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m = np.zeros(self.dim, dtype=np.float32)
        self.v = np.zeros(self.dim, dtype=np.float32)

    def update(self, theta, gradient):
        self.t += 1
        step = self._compute_step(gradient)
        # ratio = np.linalg.norm(step) / np.linalg.norm(theta)
        theta_new = theta + step
        return theta_new  # , ratio

    def _compute_step(self, gradient):
        a = self.stepsize * np.sqrt(1 - self.beta2 ** self.t) / (1 - self.beta1 ** self.t)
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradient
        self.v = self.beta2 * self.v + (1 - self.beta2) * (gradient * gradient)
        step = -a * self.m / (np.sqrt(self.v) + self.epsilon)
        return step


def compute_ranks(x):
    """
    Returns ranks in [0, len(x))
    Note: This is different from scipy.stats.rankdata, which returns ranks in [1, len(x)].
    """
    assert x.ndim == 1
    ranks = np.empty(len(x), dtype=int)
    ranks[x.argsort()] = np.arange(len(x))
    return ranks


def compute_centered_ranks(x: np.ndarray):
    """
    :param x: np.ndarray with shape (n,)
    :return:
    """
    y = compute_ranks(x).astype(np.float32)
    y /= (x.size - 1)
    y -= 0.5
    return y


def itergroups(items, group_size):
    assert group_size >= 1
    group = []
    for x in items:
        group.append(x)
        if len(group) == group_size:
            yield tuple(group)
            del group[:]
    if group:
        yield tuple(group)


def batched_weighted_sum(weights, vecs, batch_size):
    total = 0.
    num_items_summed = 0
    for batch_weights, batch_vecs in zip(itergroups(weights, batch_size), itergroups(vecs, batch_size)):
        assert len(batch_weights) == len(batch_vecs) <= batch_size
        total += np.dot(np.asarray(batch_weights, dtype=np.float32), np.asarray(batch_vecs, dtype=np.float32))
        num_items_summed += len(batch_weights)
    return total, num_items_summed
