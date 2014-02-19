#!/bin/bash
/pgm/mongodb/defalut/bin/mongod --logpath=$HOME/database/mongodb/log --logappend --fork --dbpath=$HOME/database/mongodb/data --directoryperdb --rest --auth
