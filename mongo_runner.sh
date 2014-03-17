#!/bin/bash
/opt/mongodb/default/bin/mongod --logpath=/work/database/mongodb/log --logappend --fork --dbpath=/work/database/mongodb/data --directoryperdb --rest --auth
