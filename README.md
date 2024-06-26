# smol
tiny key-value store

## Setup
### rocksdb
`brew install rocksdb`

1.	rocksdb_dump:
This tool is used to dump the contents of a RocksDB database.

```sh
rocksdb_dump --db=<path_to_your_db>
```

2.	rocksdb_ldb:
This tool provides an interactive command-line interface to perform various operations on a RocksDB database.

```
rocksdb_ldb
```

- Create a database + first key-value
```sh
# Step 1: Create a subdirectory for the database in the current directory
mkdir -p ./olivedb

# Step 2: Use rocksdb_ldb to create the database and insert a key-value pair with the create_if_missing flag
rocksdb_ldb --db=./olivedb put k1 v1 --create_if_missing

# Step 3: Verify the database creation
rocksdb_ldb --db=./olivedb get k1
```
 
Python Interface on MacOS
```
brew install rocksdb
pip install git+https://github.com/gau-nernst/rocksdb-python.git
```

## Usage

```sh
PORT=<port> ./master
```

```sh
PORT=<port> ./volume
```

### cURL
```sh
curl -X PUT -d bigswag localhost:9000/k1 -vv
curl -X DELETE http://localhost:9000/k1 -vv
curl -L GET http://localhost:9000/k1 -vv
```

## TODO
- [x] Use rocksdb
- [ ] Port to rust if python isn't fast enough
- [ ] Make fancy frontend in next + shadcn UI

