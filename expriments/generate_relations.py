import numpy as np

n = 4
d = int(np.ceil((n**2 + 1) / 4))
#calc_up_to = np.ceil((np.pi / np.arccos(n / np.sqrt(d)))) - 2
calc_up_to = np.ceil(np.pi / np.arccos(n / (2 * np.sqrt(d))))
print(calc_up_to)

elems = ['x_%d' % i for i in range(n)]

relations = []
for _ in range(d):
    rel = ''
    for i in range(n):
        for j in range(n):
            if np.random.randint(0, 2):
                #rel += "%d*%s*%s+" % (np.random.randint(0, 2), elems[i], elems[j])
                rel += "%s*%s+" % (elems[i], elems[j])
    relations.append(rel[:-1])

print(', '.join(elems))

for rel in relations:
    print(rel)
