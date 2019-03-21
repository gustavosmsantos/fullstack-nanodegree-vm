# Catalog APP #

Simple catalog project that lists pre-registered sport categories, allowing not logged in users view items created in categories, and logged in users to create and modify their own items.

## Setting up project ##

The project uses flask as web framework, and a sqlite database to persist data using sqlAlchemy. Besides that, it handles login with Oauth2 Google provider. The database should be created and google credentials configured for proper opearation.

- To initialize the database, run the command `python database-setup.py`. It creates a file named catalog.db in the root folder.
- To setup Google auth provider, include the secrets file, available to download in Google Developers Console, in the root folder named as `client_secrets.json` 
- A vagrant environment is provided with all that is required to run the application. Be sure to have Vagrant installed, and execute `vagrant up`, then `vagrant ssh` to access the machine provisioned. Run the application with command `python /vagrant/catalog/application.py`, that starts service in port 8000, and binds that port to the local machine.