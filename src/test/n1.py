#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import numpy as np


print np.version.full_version

a = np.arange(20)

print a

b = a.reshape(4, 5)
print b

print b.shape
print b.ndim
print b.size


