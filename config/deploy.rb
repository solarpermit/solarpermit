require 'mysql2'
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
  "config_it",
  "syncdb",
  "migrate_website",
  "migrate_tracking",
  "compress_jinja",
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
  if fetch(:release_name) == "Release1.3.46" then
    run "/opt/cpf/solarpermit/current/manage.py migrate website 0097"
    client = Mysql2::Client.new(:host => "localhost", :username => "root",
                                :password => fetch(:db_password),
                                :database => fetch(:db_database))
    # assume the functions were already created, and therefore might be incorrect
    client.query("DROP FUNCTION IF EXISTS json_get")
    client.query("DROP FUNCTION IF EXISTS json_valid")
    # now create them correctly
    client.query("CREATE FUNCTION json_get RETURNS string SONAME 'mysql_json.so'")
    client.query("CREATE FUNCTION json_valid RETURNS integer SONAME 'mysql_json.so'")
    # and skip the related migrations
    client.query("INSERT INTO south_migrationhistory (app_name, migration, applied) VALUES ('website', '0098_create_json_UDF_functions', NOW())")
    client.query("INSERT INTO south_migrationhistory (app_name, migration, applied) VALUES ('website', '0099_udf_function_return_type', NOW())")
    run "/opt/cpf/solarpermit/current/manage.py migrate website 0101"
    client.query("INSERT INTO south_migrationhistory (app_name, migration, applied) VALUES ('website', '0102_udf_function_return_type_utf8mb4', NOW())")
  end
  run "/opt/cpf/solarpermit/current/manage.py migrate website"
end

desc "run migrate tracking"
task :migrate_tracking do
 run "/opt/cpf/solarpermit/current/manage.py migrate tracking"
end

desc "configure site"
task :config_it do
  local_config = from_template("settings_local.py.erb")
  put local_config, "/opt/cpf/solarpermit/current/settings_local.py"
end

desc "run compress_jinja"
task :compress_jinja do
 run "/opt/cpf/solarpermit/current/manage.py compress_jinja"
end

desc "restart nginx server"
task :restart_nginx do
  sudo "/etc/init.d/nginx restart"
end

desc "restart gunicorn server"
task :restart_gunicorn do
  sudo "/etc/init.d/gunicorn-solarpermit stop"
  sudo "/etc/init.d/gunicorn-solarpermit start"
end

desc "force a chef run"
task :run_chef do
  sudo "/usr/bin/chef-client"
end

def get_binding
  binding # So that everything can be used in templates generated for the servers
end

def from_template(file)
  require 'erb'
  template = File.read(File.join(File.dirname(__FILE__), "..", file))
  result = ERB.new(template).result(self.get_binding)
end
