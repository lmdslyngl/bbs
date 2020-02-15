#!/bin/sh

createuser --createdb -U postgres bbsrole
createdb --encoding=UTF8 --locale=C --template=template0 -U bbsrole bbsdb
psql -f /bbs/dbinit.sql -U bbsrole -d bbsdb

