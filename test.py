import intopt
import numpy as np
opt = intopt.intlinprog(np.array([4200, 3000, 1600, 900, 0]),
                        A_ub=np.matrix([
                            [1, 1, 1, 1, -1],
                            [3800, 2000, 900, 900, 5000]]),
                        b_ub=np.array([2, 4800]),
                        options={'disp': True, 'branch_rule': 'max fun'})
print(opt)
print(np.floor(opt.x[0:4]) * np.array([4200, 3000, 1600, 900]).T)
