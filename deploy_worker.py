from server import server
import threading

class deploy_worker (threading.Thread):
  def __init__(self, host, port, username, path, gh_username, repo, branch):
      self.host = host
      self.port = port
      self.username = username
      self.path = path
      self.gh_username = gh_username
      self.repo = repo
      self.branch = branch
      threading.Thread.__init__(self)

  def run(self):
    s = server(self.host, self.port, self.username, None)

    try:
      if(not s.has_dir(self.path)):
        s.mkdir(self.path)
        s.init_git(self.path)
        s.add_remote(self.path, "github", "git://github.com/" + self.gh_username + "/" + self.repo + ".git")

      if not ("github" in s.get_remotes(self.path)):
        s.add_remote(self.path, "github", "git://github.com/" + self.gh_username + "/" + self.repo + ".git")

      s.pull(self.path, "github", self.branch)

      print s.stdout + "\n========\n\n" + s.stderr
    except Exception as ex:
      print ex.__str__()