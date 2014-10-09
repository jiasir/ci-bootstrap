#!/usr/bin/env python
#import os,sys,json,pycurl,cStringIO,time,urllib

import os
import sys
import logging
from jira.client import JIRA
from jenkinsapi.jenkins import Jenkins
import ConfigParser
import subprocess

def file_path(name):
	return os.path.join(
		os.path.dirname(
			os.path.abspath(__file__)),name).replace('\\','/')

config_file = ConfigParser.RawConfigParser(allow_no_value=True)
config_file.read(file_path('ci.conf'))


# Define jira
jira_url = config_file.get('jira', 'url')
jira_user = config_file.get('jira', 'user')
jira_pass = config_file.get('jira', 'pass')

# Define jenkins
jenkins_url = config_file.get('jenkins', 'url')
jenkins_user = config_file.get('jenkins', 'user')
jenkins_pass = config_file.get('jenkins', 'pass')



# create logger
logger = logging.getLogger('git-automerge')
logging.basicConfig(filename='git-automerge.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' )


# Define jira API
options = {
	'server': jira_url
}
jira_client = JIRA(options=options, basic_auth=(jira_user, jira_pass))

# Define jenkins API
jenkins = Jenkins(jenkins_url,jenkins_user,jenkins_pass)


def get_all_build_issues(project_key, version_name):
	"""
	returns only issue key list, eg) ['DEVOPS-2', 'DEVOPS-23', 'DEVOPS-33']
	"""
	issue_key_list = [issue.key for issue in jira_client.search_issues('project = %s AND issuetype in (Improvement, "New Feature", "User Bug") AND fixVersion = "%s"' % (project_key, version_name))]
	return issue_key_list



def git_create_plan_branch_if_not_exists(context):
	"""
	if no plan branch exits, git will create it. else checkout
	"""
	created = (0 == os.system('cd {git_dir} && git branch -r | grep origin/{plan_branch}'.format(**context)))
	if not created:
		if os.system('cd {git_dir} && git checkout origin/release -b {plan_branch} && git push origin {plan_branch}:{plan_branch}'.format(**context)):
			raise Exception('git_create_plan_branch_if_not_exists failed')


def shellcmd(cmd):
	proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	if proc.returncode: raise Exception('execute shell command {0} failed'.format(cmd))
	return out

def get_plan_features_from_git(context):
	out = shellcmd('cd {git_dir} && git branch -a --merged | grep remotes/origin/features/'.format(**context))
	return [branch.split('/')[3] for branch in out.split()]

def check_feature_removal(context, issue_key_list):
	current_features_of_plan = get_plan_features_from_git(context)
	removed_features = set(current_features_of_plan) - set(issue_key_list)
	if removed_features: raise Exception('Feature(s) {0} were removed from this plan!!'.format(removed_features))

def git_merge_all_feature_and_release_to_plan(context, issue_key_list):
	if os.system('cd {git_dir} && git checkout {plan_branch} && git pull && git merge -Xignore-space-change origin/release {feature_branches}'.format(**dict({
		'feature_branches': ' '.join(['origin/features/{0}'.format(key) for key in issue_key_list ])
	}.items() + context.items()))):
		raise Exception('git_merge_all_feature_and_release_to_plan failed')

def git_push_plan(context):
	if os.system('git push origin {plan_branch}:{plan_branch}'.format(**context)):
		raise Exception('git_push_plan failed')

def merge_issue_features_to_plan(project_key, version_name):
	workspace = os.environ['WORKSPACE']
	context = {
		'git_dir': workspace,
		'version_name': version_name,
		'plan_branch': 'plans/{0}'.format(version_name),
	    'project_key': project_key
	}
	issue_key_list = get_all_build_issues(project_key, version_name)
	git_create_plan_branch_if_not_exists(context)
	check_feature_removal(context, issue_key_list)
	git_merge_all_feature_and_release_to_plan(context, issue_key_list)
	git_push_plan(context)


def main(project_key, version_name):
	merge_issue_features_to_plan(project_key, version_name)

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])

