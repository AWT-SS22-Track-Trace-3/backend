#! /bin/sh

docker stop backend-tracktrace_frontend-1 backend-tracktrace_backend-1 iroha backend-mongo

docker rm -v backend-tracktrace_frontend-1 backend-tracktrace_backend-1 iroha backend-mongo backend-dbseed-1

docker volume rm backend_blockstore backend_mongodata backend_rocksdb
