import os
import yaml
import time
import hashlib
import subprocess

def get_steps(s):
	step = globals()[s['type']](**s['config'])
	return step.child_steps


class Step(object):
	def __init__(self,no_redo=False):
		self.no_redo = no_redo
		self.no_redo_file = os.environ['HOME']+'/.reinstall_lib/no_redo'
		if not hasattr(self,'cmd'):
			self.cmd = ''
		self.get_child_steps()
		self.output = 'Not executed yet: No output'
		self.exec_date = 'Not executed yet: No exec date'
		self.set_id_string()
		self.get_report()

	def get_report(self):
		ans = '\n===================\n'
		ans += self.id_string+'     '+self.cmd
		ans += '\n----------\n'
		ans += 'Exec date:' + self.exec_date
		ans += '\n----------\n'
		ans += str(self.output)
		ans += '\n===================\n'
		self.report = ans

	def get_child_steps(self):
		self.child_steps = [self]

	def process(self):
		if self.no_redo:
			with open(os.environ['HOME']+'/.reinstall_lib/no_redo', 'a'):
				f.write(self.id+'   '+self.cmd)
		self.exec_date = time.strftime('%Y-%m-%d_%H-%M-%S')
		if not self.no_redo or not self.check_executed():
			self.execute()
		else:
			self.output = 'Already executed'

		self.get_report()


	def execute(self):
		pass

	def set_id_string(self):
		self.id_string = hashlib.md5(self.cmd.encode()).hexdigest()

	def check_executed(self):
		if not os.exists(self.no_redo_file):
			return False
		else:
			with open(self.no_redo_file,'r') as f:
				id_list = f.read().split('\n')[:32]
			if self.id_string in id_list:
				return True
			else:
				return False

	def splitted_cmd(self):
		return self.cmd.split(' ')


class ReinstallProcess(object):
	def __init__(self,filename):
		try:
			os.makedirs(os.environ['HOME']+'/.reinstall_lib')
		except FileExistsError:
			pass
		with open(filename,'r') as f:
			self.info = yaml.load(f.read())
			print(self.info)
		self.steps = []
		self.name = time.strftime('%Y-%m-%d_%H-%M-%S')

	def build_steps(self):
		for s in self.info:
			self.steps += get_steps(s)

	def write_report(self,report,failed=False):
		with open(os.environ['HOME']+'/.reinstall_lib/'+self.name,'a') as f:
			f.write(report)
		if failed:
			with open(os.environ['HOME']+'/.reinstall_lib/'+self.name+'_failed','a') as f:
				f.write(report)

	def write_all_reports(self):
		for s in self.steps:
			self.write_report(s.report)

	def read_report(self):
		with open(os.environ['HOME']+'/.reinstall_lib/'+self.name,'r') as f:
			print(f.read())


	def execute_process(self):
		for s in self.steps:
			s.process()
			self.write_report(s.report,failed= not s.success)
		self.write_report('Ended at '+time.strftime('%Y-%m-%d_%H-%M-%S'))


class CmdStep(Step):
	def __init__(self,cmd,**kwargs):
		self.cmd = cmd
		Step.__init__(self,**kwargs)

	def execute(self):
		cmd2 = self.splitted_cmd()
		try:
			self.output = subprocess.check_output(cmd2).decode('utf-8')
			self.success = True
		except Exception as e:
			self.success = False
			self.output = str(e)


####### APT

class APTUpdate(CmdStep):
	def __init__(self):
		cmd = 'sudo apt-get -y update'
		CmdStep.__init__(self,cmd=cmd)

class APTUpgrade(CmdStep):
	def __init__(self):
		cmd = 'sudo apt-get -y upgrade'
		CmdStep.__init__(self,cmd=cmd)

class APTStep(CmdStep):
	def __init__(self,package):
		cmd = 'sudo apt-get -y install '+package
		CmdStep.__init__(self,cmd=cmd)

class MultiAPTStep(APTStep):
	def __init__(self,packages):
		if isinstance(packages,list):
			self.packages = packages
		else:
			self.packages = packages.split(' ')
		Step.__init__(self)

	def get_child_steps(self):
		self.child_steps = [APTStep(package = p) for p in self.packages ]


class APTrepoStep(CmdStep):#add key?
	def __init__(self,repo):
		self.repo = repo
		cmd = 'sudo apt-add-repository -y install '+repo
		CmdStep.__init__(self,cmd=cmd,no_redo=True)

	def splitted_cmd(self):
		if '"' not in self.cmd:
			return CmdStep.splitted_cmd(self.cmd)
		else:
			splits = self.cmd.plit('"')
			return CmdStep.splitted_cmd(splits[0])+['"'+splits[1]+'"']+CmdStep.splitted_cmd(splits[2])

class APTrepoUndoStep(APTrepoStep):
	def __init__(self,repo):
		self.repo = repo
		cmd = 'sudo apt-add-repository --remove '+repo
		CmdStep.__init__(self,cmd=cmd,no_redo=True)




class APTUndoStep(CmdStep):
	def __init__(self,package):
		cmd = 'sudo apt-get -y remove '+package
		CmdStep.__init__(self,cmd=cmd)

class MultiAPTUndoStep(MultiAPTStep):
	def get_child_steps(self):
		self.child_steps = [APTUndoStep(package = p) for p in self.packages ]


####### PIP and Python

class PIPStep(CmdStep):#2 or 3 or both
	def __init__(self,package,version=3,both=False):
		if version not in [2,3]:
			raise ValueError('pip version should be 2 or 3')
		self.version = version
		self.both = both
		self.package = package
		cmd = self.gen_cmd()
		CmdStep.__init__(self,cmd=cmd)

	def gen_cmd(self):
		return 'sudo pip'+self.version+' -U install '+package

	def get_child_steps(self):
		if self.both:
			if self.version == 2:
				version = 3
			else:
				version = 2
			self.child_steps = [self,self.__class__(package=self.package,version=version,both=False)]
		else:
			self.child_steps = [self]

class PIPUndoStep(PIPStep):
	def gen_cmd(self):
		return 'sudo pip'+self.version+' uninstall '+package

class MultiPIPStep(PIPStep):
	def __init__(self,packages,version=3,both=False):
		self.packages = packages
		self.version = version
		self.both = both
		Step.__init__(self)

	def get_child_steps(self):
		self.child_steps = [PIPStep(package = p,both=self.both,version=self.version) for p in self.packages ]

class MultiPIPUndoStep(MultiPIPStep):
	def get_child_steps(self):
		self.child_steps = [PIPUndoStep(package = p,version=self.version,both=self.both) for p in self.packages ]







class InstallPython(Step):
	def __init__(self):
		pass


class InstallJupyter(Step):
	def __init__(self):
		pass

class MoveConfig(Step):
	def __init__(self):
		pass

class CreateSSH(Step):
	def __init__(self):
		pass
class MoveSSH(Step):
	def __init__(self):
		pass

class FirewallConfig(CmdStep):
	def __init__(self):
		pass