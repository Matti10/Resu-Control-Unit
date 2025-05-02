from RCU import RCU
from static import *
import asyncio

rcu = RCU()

asyncio.run(rcu.init_all_RCUFuncs())

asyncio.get_event_loop().run_forever()
