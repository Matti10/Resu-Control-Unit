import RCU
from static import *
import asyncio

rcu = RCU.RCU()

sl = rcu.add_RCUFunc(SHIFTLIGHT_TYPE)
asyncio.run(rcu.init_all_RCUFuncs())

rcu.export_config(configPath="/workspaces/Resu-Control-Unit/src/data/test-config.json")