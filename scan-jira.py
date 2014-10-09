#!/usr/bin/env python
# TODO automaticly install dependencies, example: django
#import os,sys,json,time,pycurl,cStringIO,jenkinsapi,django
import os
import sys, traceback
import logging
import jira
from jira.client import JIRA
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
import json
import django
from django.template import loader, Template, Context
from django.conf import settings
import ConfigParser
import re
import StringIO


def file_path(name):
	return os.path.join(
		os.path.dirname(
			os.path.abspath(__file__)),name).replace('\\','/')

# create logger
logger = logging.getLogger('scan-jira')
logging.basicConfig(filename='scan-jira.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' )

config_file = ConfigParser.RawConfigParser(allow_no_value=True)
config_file.read(file_path('ci.conf'))

settings.configure()

settings.TEMPLATE_DIRS = (file_path('templates'),)




#jenkins test server is http://192.168.1.152:8080/, username is admin, password is shangpin@123

# Define jira
jira_url = config_file.get('jira', 'url')
logger.debug('jira url: {0}'.format(jira_url))
jira_user = config_file.get('jira', 'user')
logger.debug('jira user: {0}'.format(jira_user))
jira_pass = config_file.get('jira', 'pass')

# Define jenkins
jenkins_url = config_file.get('jenkins', 'url')
logger.debug('jenkins url: {0}'.format(jenkins_url))
jenkins_user = config_file.get('jenkins', 'user')
logger.debug('jenkins user: {0}'.format(jenkins_user))
jenkins_pass = config_file.get('jenkins', 'pass')

email_list = config_file.get('job', 'email')


def extract_build_config_from_description(description):
	r = re.compile('(?ms)(<!--build\r?\n(.*)-->)|(<pre type=.build.>\r?\n(.*)</pre>)')
	match = r.findall(description)
	if not match: raise Exception('No build config in project description!!')

	config_str = match[0][1] or match[0][3]
	logger.debug('project build config from description:\n{0}\n'.format(config_str))
	config_stream = StringIO.StringIO(config_str)
	build_config = ConfigParser.RawConfigParser(allow_no_value=True)
	build_config.readfp(config_stream)
	return build_config


def create_job_for_version(project, version, jenkins):
	job_name = '{0}-{1}'.format(project.key, version.name)
	logger.debug("Create job: {0}".format(job_name))

	if job_name in jenkins.keys():
		logger.debug('{0} has already in jenkins.'.format(job_name))
		return

	if not hasattr(project, 'url') or not project.url:	raise Exception('No url for project!!')

	build_config = extract_build_config_from_description(project.description)
	build_profile = build_config.get('default', 'profile')
	logger.debug('project build profile is {0}'.format(build_profile))
	template = loader.get_template('profiles/{0}.xml'.format(build_profile))
	context_dict = dict({
			'job_name': job_name,
			'branch_name': 'plans/{0}'.format(version.name),
			'email_list': email_list,
			'git_url': '{0}.git'.format(project.url),
			'py_command': 'python ${{WORKSPACE}}/../../tools/ci-bootstrap/git-automerge.py {0}'.format(' '.join([project.key, version.name]))
		}.items() + build_config.items('context'))
	logger.debug('template context is:\n{0}\n'.format(context_dict))
	context = Context(context_dict)
	config = template.render(context)
	
	logger.debug('Founded a new version {0} of project: {1}, The job will be created and build.'.format(version.name, project.key))

	jenkins.create_job(job_name, config)
	jenkins.build_job(job_name)

def main():
	jira = JIRA(options={'server': jira_url}, basic_auth=(jira_user, jira_pass))
	jenkins = Jenkins(jenkins_url,jenkins_user,jenkins_pass)

	logger.info('Get all projects')
	projects = jira.projects()

	logger.info('Get all versions')
	#key: <JIRA Project: key=u'SE', name=u'\u641c\u7d22\u5f15\u64ce', id=u'10750'>
	#value: [<JIRA Version: name=u'v1.0', id=u'11312'>, ...]
	project_version_map = dict(
		[
			z for z in zip(
				[jira.project(project.id) for project in projects],
				[jira.project_versions(p.id) for p in projects]
			)
			if len(z[1]) !=0
		])
	logger.debug("All project and its versions: {0}".format(project_version_map))
	
	
	for project, versions in project_version_map.items():
		for version in versions:
			try:
				create_job_for_version(project, version, jenkins)
			except Exception as e:
				logger.critical('failed to create job: {0}!! Reason: \n{1}'
								.format(project.key,
										''.join(traceback.format_exception(*sys.exc_info()))))

	
if __name__ == '__main__':
	main()
