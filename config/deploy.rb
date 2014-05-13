require 'capistrano/ext/multistage'
default_run_options[:pty] = true

##################
# global configs #
##################
#
set :stages, ["dev", "stg", "prod"]
set :use_sudo, false

set :application, "solarpermit"
set :scm, :git
set :repository, "git@github.com:CleanPowerFinance/solarpermit.git"
set :deploy_via, :remote_cache
set :branch, "master"

set :user, "www-data"
set :applicationdir, 'solarproconnect'
set :keep_releases, 8
set :deploy_to, "/opt/cpf/#{application}"

set(:previous_release) { releases[0,releases.length-1].grep(/Release/).length > 0 ? File.join(releases_path, releases[0,releases.length-1].grep(/Release/).last) : nil }

####################
# config overrides #
####################
if exists? :force_branch
  set :branch, force_branch
  # Set release_name if force_branch is set, this will label the release dir
  if force_branch =~ /^Release/
    set :release_name, force_branch
  end
elsif ENV['FORCE_BRANCH']
  set :branch, ENV['FORCE_BRANCH']
  # Same as above for naming release dir
  if force_branch =~ /^Release/
    set :release_name, ENV['FORCE_BRANCH']
  end
end


################
# deploy tasks #
################
#before :deploy, "verify_deploy_request"
#after "deploy:finalize_update"

after :deploy,
  "syncdb",
  "migrate_website",
  "migrate_tracking",
  "migrate_compress_jinja",
  "restart_gunicorn",
  "restart_nginx",
  "run_chef"

#not sure if this is needed.... 
desc "run syncdb"
task :syncdb do
  run "/opt/cpf/solarpermit/current/manage.py syncdb"
end

desc "run migrate website"
task :migrate_website do
 run "/opt/cpf/solarpermit/current/manage.py migrate website"
end

desc "run migrate tracking"
task :migrate_tracking do
 run "/opt/cpf/solarpermit/current/manage.py migrate tracking"
end

desc "run migrate compress_jinja"
task :migrate_compress_jinja do
 run "/opt/cpf/solarpermit/current/manage.py migrate compress_jinja"
end

desc "restart nginx server"
task :restart_nginx do
  sudo "/etc/init.d/nginx restart"
end

desc "restart gunicorn server"
task :restart_gunicorn do
  sudo "/etc/init.d/gunicorn-solarpermit restart"
end

desc "force a chef run"
task :run_chef do
  sudo "/usr/bin/chef-client"
end

