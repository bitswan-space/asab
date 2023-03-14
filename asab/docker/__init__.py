import logging
import os

from ..abc.module import Module
from ..config import Config

from .service import DockerService

#

L = logging.getLogger(__name__)

#

Config.add_defaults(
	{
		'docker': {
			# Docker API or socket
			# Could be `http://myHost:2375` or `/var/run/docker.sock`
			'socket': '',
		}
	}
)


def running_in_container():

	if os.path.exists('/.dockerenv') and os.path.isfile('/proc/self/cgroup'):
		with open('/proc/self/cgroup', "r") as f:
			if any('docker' in line for line in f.readlines()):
				return True

	# since Ubuntu 22.04 linux kernel uses cgroups v2 which do not operate with /proc/self/cgroup file
	if os.path.isfile('/proc/self/mountinfo'):
		with open('/proc/self/mountinfo', "r") as f:
			for line in f.readlines():
				# Seek for a root filesystem
				if ' / / ' not in line:
					continue

				# Is the root filesystem runs on overlay?
				if ' overlay ' not in line:
					continue

				return True

	return False


running_in_docker = running_in_container


class Module(Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = DockerService(app, "asab.DockerService")
