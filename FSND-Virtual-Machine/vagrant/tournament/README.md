# Tournament Results

This project uses Python and PostgreSQL database to keep track of players and matches in a game tournament. The tournament uses Swiss system for pairing up players in each round.  

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

```
Python 2.7.9
```
Vagrant Virtual Machine

### Installing

* Go to https://cloud.google.com/appengine/docs/standard/python/download
* Follow https://www.python.org/downloads/ to install Python
* Follow http://sourabhbajaj.com/mac-setup/Vagrant/README.html to install Vagrant

## Running the program

* Open the command line terminal and navigate into the folder vagrant
* Run 'vagrant up' to start the machine
* Run 'vagrant ssh' to ssh into the machine
* Run 'cd /vagrant' to go into vagrant folder
* Run 'CREATE DATABASE tournament;' to create a database
* Run 'cd tournament' to go into tournament folder
* Run 'psql' to start the database
* Run '\i tournament.sql' to create tables in the database
* Run 'control + D' to exit out of the database
* Run 'python tournament_test.py' to run the program
