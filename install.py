#!/usr/bin/env python

from util import Util
from command import Command

Util.config_jira()
Util.config_email()
Util.config_jenkins()

def install_dependencies(pip, django, jenkinsapi, jira):
	Command.execute('sudo', 'apt-get', '-y', 'install', pip)
	Command.execute('sudo', 'pip', 'install', django)
	Command.execute('sudo', 'pip', 'install', jenkinsapi)
	Command.execute('sudo', 'pip', 'install', jira)
		
def main():
	install_dependencies('pip', 'django', 'jenkinsapi', 'jira')
	xml = Util.get_xml_content('jira-scan.xml')
	Util.create_job('ci-bootstrap', xml)
	Util.build_job('ci-bootstrap')

if __name__ == '__main__':
	main()