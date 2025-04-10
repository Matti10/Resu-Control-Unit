import RCU
from static import *
import asyncio

rcu = RCU.RCU()

sl = rcu.add_RCUFunc(SHIFTLIGHT_TYPE)
rpm = rcu.add_RCUFunc(RPMREADER_TYPE)
asyncio.run(rcu.init_all_RCUFuncs())

# sl.sample_pattern(PATTERN_LR)
sl.sample_brightness(1, 0.5)