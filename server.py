import paramiko

class server:
	def __init__(self, host, port, username, password=None):

		self.ssh = paramiko.SSHClient()

		# Since we're just going to be executing some simple commands,
		# there's no reason to enforce host key checks.
		self.ssh.set_missing_host_key_policy(
			paramiko.AutoAddPolicy())

		# Now connect to the server!
		self.ssh.connect(host, port=port, username=username,
			password=password, look_for_keys=False, timeout=30,
			key_filename="/home/gitdeploy/.ssh/id_dsa")

		self.stderr = ""
		self.stdout = ""

	def _exec(self, command, log=False):
		stdin, stdout, stderr = self.ssh.exec_command(command)
		self._log_errors(stderr)

		lines = "".join(stdout.readlines())

		if(log):
			self.stdout = self.stdout + lines

		return lines

	def _exec_dir(self, command, dir, log=False):
		if(not self.has_dir(dir)):
			raise IOError(dir + ' does not exist!')

		return self._exec("cd " + dir + "; " + command, log)

	def _log_errors(self, stderr):
		lines = stderr.readlines()

		if(len(lines) > 0):
			# paramiko leaves the trailing \ns on the lines, so no
			# need to remove them ourselves.
			self.stderr = self.stderr + ("".join(lines))

	def mkdir(self, dir):
		self._check_dir(dir)

		self._exec('mkdir "' + dir + '"')

	def mv_dir(self, old, new):

		# Checking if the directories exist will handle input validation for us.
		if(not self.has_dir(old)):
			raise IOError(old + " does not exist")
		if(self.has_dir(new)):
			raise IOError(new + " exists")

		self._exec('mv "' + old + '" "' + new + '"')

	def init_git(self, dir):
		self._exec_dir("git init", dir, True)

	def get_remotes(self, dir):
		return filter(None, self._exec_dir("git remote", dir).split("\n"))

	def get_remote_pull(self, dir, remote):
		if(not remote.isalnum() or len(remote) == 0):
			raise ValueError("Remote name must be alphanumeric")

		return self._exec_dir("git remote show " + remote, dir).split("\n")[1].split(': ')[1]

	def add_remote(self, dir, name, path):
		if(path.replace(';', '').replace(' ', '').replace('#', '') != path):
			raise ValueError("Invalid path")

		if(not name.isalnum()):
			raise ValueError("Name must be alphanumeric")

		self._exec_dir("git remote add " + name + " " + path, dir, True)

	def pull(self, dir, remote, branch):
		if(not remote.isalnum() or not branch.isalnum() or len(remote) == 0 or len(branch) == 0):
			raise ValueError("Remote and branch names must be alphanumeric")

		return self._exec_dir("git pull " + remote + " " + branch, dir, True)

	def has_dir(self, dir):
		self._check_dir(dir)

		exists = self._exec('[ -d ' + dir + ' ] && echo "Directory exists" || echo "Directory does not exist"')
		return len(exists) > 0 and exists.find("Directory exists") >= 0

	def _check_dir(self, dir):
		sanDir = dir.replace('/', '').replace(' ', '').replace('-', '').replace('_', '').replace('.', '')
		if(not sanDir.isalnum() or not len(sanDir) > 0 or dir[0] != '/'):
			raise ValueError("Directory can only contain alphanumeric characters, spaces, /, _, and -; must start with a leading slash; and must not be /. Given was " + dir)

	def has_git(self):
		which = self._exec("which git");
		return len(which) > 0 and which[0] == "/"

	def close(self):
		self.ssh.close()

	def get_os(self):
		oses = [
			'Mint', 'Ubuntu', 'Fedora', 'SUSE', 'Debian', 'Arch', 'CentOS', 'Mageia', 'Puppy',
			'PCLinuxOS', 'Lubuntu', 'FreeBSD', 'Sabayon', 'Chakra', 'Ultimate', 'Bodhi',
			'Mandriva', 'Slackware', 'PC-BSD', 'Gentoo', 'Funduntu', 'Zorin', 'Pinguy', 'Scientific',
			'ArchBang', 'Tiny Core', 'Kubuntu', 'Vector', 'GhostBSD', 'CrunchBang', 'Xubuntu',
			'Red Hat', 'Pear', 'KNOPPIX', 'Dreamlinux', 'BackTrack', 'ClearOS', 'MEPIS', 'Tails',
			'Salix', 'Unity', 'Frugalware', 'FreeNAS', 'Ubuntu Studio', 'Peppermint', 'Dream Studio',
			'ZevenOS', 'Commodore', 'BackBox', 'Solaris'
			]

		distro_info = self._exec("cat /etc/*-release")

		for os in oses:
			if(distro_info.lower().find(os.lower()) >= 0):
				return os

		return "Unknown"