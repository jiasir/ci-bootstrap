from jira.client import JIRA
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
import django
from django.template import loader, Template, Context
from django.conf import settings
import ConfigParser


class Util:
	
	def __init__(self):
		logging.basicConfig(filename='scan-jira.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
		self.logger = logging.getLogger('util.Util')
		
		self.config_file = ConfigParser.RawConfigParser(allow_no_value=True)
		self.config_file.read('ci.conf')

		settings.configure()

		settings.TEMPLATE_DIRS = (file_path('templates'),)
		

		Util._jira_obj = config_jira()
		Util._jenkins_obj = config__jenkins()

	def jira():
		return Util._jira_obj
	
	def jenkins():
		return Util._jenkins_obj

	def config_jira(self):
		"""Returns a jira object."""
		self.jira_url = config_file.get('jira', 'url')
		self.logger.debug('jira url: {0}'.format(jira_url))
		self.jira_user = config_file.get('jira', 'user')
		self.logger.debug('jira user: {0}'.format(jira_user))
		self.jira_pass = config_file.get('jira', 'pass')
		return JIRA(options={'server': jira_url}, basic_auth=(jira_user, jira_pass))
	
	def config_jenkins(self):
		"""Returns a jenkins object."""
		self.jenkins_url = config_file.get('jenkins', 'url')
		self.logger.debug('jenkins url: {0}'.format(jenkins_url))
		self.jenkins_user = config_file.get('jenkins', 'user')
		self.logger.debug('jenkins user: {0}'.format(jenkins_user))
		self.jenkins_pass = config_file.get('jenkins', 'pass')
		self.jenkins = Jenkins(jenkins_url,jenkins_user,jenkins_pass)
		return self.jenkins()
