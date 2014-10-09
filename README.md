ci-bootstrap
============

A devops tools automates the lifecycle of provisioning, orchestration and go live.

### Overview
This open source project will help you to automates your devops lifecycle for your enterprise that are provisioning stage, orchestration stage, monitoring and go live.

### Components and features
* Some puppet language and python, a bit go language for high concurrency to muti-deploy.
* Provisioning stage using our puppt-openstack project(github.com/nofdev/puppet-openstack) for OpenStack Havana and IceHouse.
* Improve the jenkins for scan the jira job to the git environment, and create a branch for testing and production.
* The production branch will auto go live for production environments, compatibility LVS and Keepalived configuration automation.
* Auto monitoring the production branch you have go lived.


### Core Project Authors
pottow (Richard Zhang) <pootow@gmail.com> SHANGPIN Crop. R&D Director
jiasir (Taio Jia) <jiasir@icloud.com> SHANGPIN Crop. Ops Manager
mengqiang81 (Qiang Meng) <mengqiang81@gmail.com> BEIFU, Chief Architect
