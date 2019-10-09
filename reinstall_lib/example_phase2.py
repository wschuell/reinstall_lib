
from __init__ import ReinstallProcess

rp = ReinstallProcess('reinstall.yml')

rp.build_steps()

rp.write_all_reports()
rp.execute_process()

rp.read_report()