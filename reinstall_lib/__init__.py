import os
import yaml
import time


def get_steps(s):
	step = locals()[s['type']](**s['config'])
	return step.child_steps


class Step(object):
	def __init__(self,no_redo=False):
		self.no_redo = no_redo
		self.no_redo_file = '~/.reinstall_lib/no_redo'
		self.get_child_steps()

	def get_report(self):
		ans = '==================='
		ans += self.id+'     '+self.cmd
		ans += '----------'
		ans += 'Exec date:' + self.exec_date
		ans += '----------'
		ans += self.output
		ans += '==================='
		self.report = ans

	def get_child_steps(self):
		self.child_steps = [self]

	def process(self):
		if self.no_redo:
			with open('~/.reinstall_lib/no_redo', 'a'):
				f.write(self.id+'   '+self.cmd)
		self.exec_date = time.strftime('%Y-%m-%d_%H-%M-%S')
		if not self.no_redo or not self.check_executed():
			self.execute()
		else:
			self.output = 'Already executed'


	def execute(self):
		pass

	def set_id_string(self):
		self.id_string = 

	def check_executed(self):
		if not os.exists(self.no_redo_file):
			return False
		else:
			with open(self.no_redo_file,'r') as f:
				id_list = f.read().split('\n')[:16]
			if self.id_string in id_list:
				return True
			else:
				return False



class Reinstall_Process(object):
	def __init__(self,filename):
		os.makedirs('~/.reinstall_lib')
		with open(filename,'r') as f:
			self.info = yaml.load(f.read(filename))
		self.steps = []
		self.name = time.strftime('%Y-%m-%d_%H-%M-%S')

	def build_steps(self):
		for s in self.info:
			self.steps += get_step(s)

	def write_report(self,report):
		with open('~/.reinstall_lib/'+self.name,'a') as f:
			f.write(report)

	def execute_process(self):
		for s in self.steps:
			s.process()
			self.write_report(s.report)
		self.write('Ended at '+time.strftime('%Y-%m-%d_%H-%M-%S'))

class APTrepoStep(Step):
class APTrepoUndoStep(Step):
class APTStep(Step):
class APTUndoStep(Step):

class PIPUndoStep(Step):
class PIPStep(Step):#2 or 3 or both

class InstallPython(Step):

class InstallJupyter(Step):

class CmdStep(Step):
	def __init__(self,cmd,**kwargs):
		self.cmd = cmd
		Step.__init__(self,**kwargs)

	def execute(self):
		self.output = subprocess.check_output(cmd2)

class MoveConfig(Step):

class CreateSSH(Step):
class MoveSSH(Step):

class FirewallConfig(Step):