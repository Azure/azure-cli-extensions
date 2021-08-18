# Heroku CLI vs. Azure CLI

| Scope | Heroku Group | Heroku Command | Description | CLI Group | CLI Command |
|---|---|---|---|---|---|
|Space|spaces||list available spaces
|||create       |create a new space
|||destroy      |destroy a space
|||info         |show info about a space
|||peering      |display the information necessary to initiate a peering connection
|||peerings     |list peering connections for a space
|||ps           |list dynos for a space
|||rename       |renames a space
|||topology     |show space topology
|||transfer     |transfer a space to another team
|||vpn          |display the configuration information for VPN
|||wait         |wait for a space to be created
|Dyno|ps||list dynos for an app
|||autoscale        |disable web dyno autoscaling
|||copy             |Copy a file from a dyno to the local filesystem
|||exec             |Create an SSH session to a dyno
|||forward          |Forward traffic on a local port to a dyno
|||kill             |stop app dyno
|||resize           |manage dyno sizes
|||restart          |restart app dynos
|||scale            |scale dyno quantity up or down
|||socks            |Launch a SOCKS proxy into a dyno
|||stop             |stop app dyno
|||type             |manage dyno sizes
|||wait             |wait for all dynos to be running latest version after a release
||run||run a one-off process inside a heroku dyno
|||detached         |run a detached dyno, where output is sent to your logs
|App|apps||list your apps
|||create       |creates a new app|webapp|create|
|||destroy      |permanently destroy an app|webapp|delete|
|||info         |show detailed app information|webapp|show|
|||open         |open the app in a web browser|webapp|browse|
|||stacks       |show the list of available stacks|webapp|x|
|||rename       |rename an app|webapp|x|
|||errors       |view app errors|webapp|x|
|||favorites    |list favorite apps|webapp|x|
||config||display the config vars for an app
|||edit         |interactively edit config vars
|||get          |display a single config value for an app
|||set          |set one or more config vars
|||unset        |unset one or more config vars
||domains||list domains for an app
|||add|add a domain to an app
|||clear        |remove all domains from an app
|||info         |show detailed information for a domain
|||remove       |remove a domain from an app
|||update       |update a domain to use a different SSL cert
|||wait         |wait for domain to be active for an app
||features||list available app features
|||disable      |disables an app feature
|||enable       |enables an app feature
|||info         |display information about a feature
||labs||list experimental features
|||disable      |disables an experimental feature
|||enable       |enables an experimental feature
|||info         |show feature info
||drains||display the log drains of an app
|||add          |adds a log drain to an app
|||remove       |removes a log drain from an app
||logs|         |display recent log output
||maintenance||display the current maintenance status of app
|||on           |take the app out of maintenance mode
|||off          |put the app into maintenance mode
||notifications||display notifications
||webhook||list webhooks on an app
|||add         |add a webhook to an app
|||deliveries  |list webhook deliveries on an app
|||events      |list webhook events on an app
|||info        |info for a webhook on an app
|||remove      |removes a webhook from an app
|||update      |updates a webhook in an app
|Addons|addons||lists your add-ons and attachments
|||attach   |attach an existing add-on resource to an app       |connection|create|
|||detach   |detach an existing add-on resource from an app     |connection|delete|
|||info     |show detailed attachment information               |connection|show|
|||services |list all available add-on services                 |connection|list-support-types|
|||create   |create a new add-on resource                       |√|√|
|||wait     |show provisioning status of the add-ons on the app |√|√|
|||destroy  |permanently destroy an add-on resource             |√|√|
|||docs     |open an add-on's documentation in browser          |√|√|
|||rename   |rename an add-on                                   |{target}|x|                 
|||open     |open an add-on's dashboard in your browser         |{target}|x|
|||downgrade|change add-on plan                                 |{target}|update|
|||upgrade  |change add-on plan                                 |{target}|update|
|||plans    |list all available plans for an add-on services    |{target}|x|
||pg||show database information                                 |postgres|
|||backups             |list database backups
|||bloat               |show table and index bloat in your database ordered by most wasteful
|||blocking            |display queries holding locks other queries are waiting to be released
|||connection-pooling  |add an attachment to a database using connection pooling
|||copy                |copy all data from source db to target
|||credentials         |show information on credentials in the database
|||diagnose            |run or view diagnostics report
|||info                |show database information
|||kill                |kill a query
|||killall             |terminates all connections for all credentials
|||links               |lists all databases and information on link
|||locks               |display queries with active locks
|||maintenance         |show current maintenance information
|||outliers            |show 10 queries that have longest execution time in aggregate
|||promote             |sets DATABASE as your DATABASE_URL
|||ps                  |view active queries with execution time
|||psql                |open a psql shell to the database
|||pull                |pull Heroku database into local or remote database
|||push                |push local or remote into Heroku database
|||reset               |delete all data in DATABASE
|||settings            |show your current database settings
|||unfollow            |stop a replica from following and make it a writeable database
|||upgrade             |unfollow a database and upgrade it to the latest stable PostgreSQL version
|||vacuum-stats        |show dead rows and whether an automatic vacuum is expected to be triggered
|||wait                |blocks until database is available
||redis||gets information about redis                           |redis|
|||cli                        |opens a redis prompt
|||credentials              |display credentials information
|||info                     |gets information about redis
|||keyspace-notifications   |set the keyspace notifications configuration
|||maintenance              |manage maintenance windows
|||maxmemory                |set the key eviction policy
|||promote                  |sets DATABASE as your REDIS_URL
|||stats-reset              |reset all stats covered by RESETSTAT
|||timeout                  |set the number of seconds to wait before killing idle connections
|||wait                     |wait for Redis instance to be available
||psql||open a psql shell to the database
|Building|buildpacks||display the buildpacks for an app
|||add          |add new app buildpack
|||clear        |clear all buildpacks set on the app
|||info         |fetch info about a buildpack
|||remove       |remove a buildpack set on the app
|||search       |search for buildpacks
|||set          |set a buildpacks set on the app
|||versions     |list versions of a buildpack
||local||run heroku app locally
|||run          |run a one-off command
|||version      |display node-foreman version
|Deployment|container||Use containers to build and deploy Heroku apps
|||login        |log in to Heroku Container Registry
|||logout       |log out from Heroku Container Registry
|||pull         |pulls an image from an app's process type
|||push         |pushes Docker images to deploy the app
|||release      |releases previously pushed Docker images
|||rm           |remove the process type from your app
|||run          |builds and runs the docker image locally
||git||manage local git repository for app
|||clone        |clones a heroku app
|||remote       |adds a git remote to an app repo
||regions||list available regions for deployment
|CI/CD|pipelines||list pipelines you have access to
|||add          |add this app to a pipeline
|||connect      |connect a github repo to an existing pipeline
|||create       |create a new pipeline
|||destroy      |destroy a pipeline
|||diff         |compares the latest release of this app to its downstream app(s)
|||info         |show list of apps in a pipeline
|||open         |open a pipeline in dashboard
|||promote      |promote the latest release of this app to its downstream app(s)
|||remove       |remove this app from its pipeline
|||rename       |rename a pipeline
|||setup        |bootstrap a new pipeline with common settings and create a production and staging app (requires a fully formed app.json in the repo)
|||transfer     |transfer ownership of a pipeline
|||update       |update the app's stage in a pipeline
||ci||display the most recent CI runs for the given pipeline
|||info             |show the status of a specific test run
|||last             |looks for the most recent run
|||rerun            |rerun tests against current directory
|||run              |run tests against current directory
|||config           |display CI config vars
|||debug            |opens an interactive debugging session
|||migrate-manifest |migrate app-ci.json to app.json
|||open             |open the Dashboard version of Heroku CI
||releases||display the releases for an app
|||info         |view detailed information for a release
|||output       |View the release command output
|||rollback     |rollback to a previous release
||reviewapps||manage reviewapps in pipelines
|||disable      |disable review apps and/or settings on an existing pipeline
|||enable       |enable review apps and/or settings on an existing pipeline
|Collaboration|apps|join|add yourself to a team app
|||leave        |remove yourself from a team app
|||lock         |prevent team members from joining an app
|||unlock       |unlock an app so any team member can join
|||transfer     |transfer applications to another user or team
||access||list who has access to an app
|||add          |add new users to your app
|||remove       |remove users from a team app
|||update       |update existing collaborators on an team app
||members||list members of a team
|||add          |adds a user to a team
|||remove       |removes a user from a team
|||set          |sets a members role in a team
||orgs||list the teams that you are a member of
|||open         |open the team interface in a browser window
||teams||list the teams that you are a member of
|Security|auth||check 2fa status
|||2fa          |check 2fa status
|||login        |login with your Heroku credentials
|||logout       |clears local login credentials 
|||token        |outputs current CLI authentication token
|||whoami       |display the current logged in user
||authorizations||list OAuth authorizations
|||create       |create a new OAuth authorization
|||info         |show an existing OAuth authorization
|||revoke       |revoke OAuth authorization
|||rotate       |updates an OAuth authorization token
|||update       |updates an OAuth authorization
||clients||list your OAuth clients
|||create       |create a new OAuth client
|||destroy      |delete client by ID
|||info         |show details of an oauth client
|||rotate       |rotate OAuth client secret
|||update       |update OAuth client
||keys|add      |add an SSH key for a user
|||clear        |remove all SSH keys for current user
|||remove       |remove an SSH key from the user
||certs||list SSL certificates for an app
|||add          |add an SSL certificate to an app
|||auto         |show ACM status for an app
|||chain        |print an ordered chain for a cert
|||generate     |generate a key & a CSR or self-signed cert
|||info         |show certificate information
|||key          |print the correct key for the given cert
|||remove       |remove an SSL certificate from an app
|||update       |update an SSL certificate on an app
||sessions||list your OAuth sessions
|||destroy      |delete (logout) OAuth session by ID
|Health|status||display current status of the Heroku platform
|CLI|help||display help for heroku|
||plugins||list installed plugins
|||install      |installs a plugin into the CLI
|||link         |links a plugin into the CLI for development
|||uninstall    |removes a plugin from the CLI
|||update       |update installed plugins
||update||update the Heroku CLI
||autocomplete||display autocomplete installation instructions