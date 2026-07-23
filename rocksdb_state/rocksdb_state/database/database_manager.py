class DatabaseManager:
    """
    Manages the RocksDB lifecycle.
    Note: For local Windows development (to bypass python-rocksdb build failures),
    this currently mocks the storage engine using an in-memory dictionary.
    In a true production environment, this would wrap `rocksdb.DB`.
    """
    
    def __init__(self, db_path: str = "./rocksdb_data"):
        self.db_path = db_path
        self._store = {}
        self._is_open = False
        
    def open(self):
        """Opens the database connection."""
        self._is_open = True
        # In a real implementation:
        # self._db = rocksdb.DB(self.db_path, rocksdb.Options(create_if_missing=True))
        
    def close(self):
        """Closes the database connection."""
        self._is_open = False
        self._store.clear()
        
    def put(self, key: bytes, value: bytes):
        if not self._is_open:
            raise RuntimeError("Database is closed")
        self._store[key] = value
        
    def get(self, key: bytes) -> bytes:
        if not self._is_open:
            raise RuntimeError("Database is closed")
        return self._store.get(key)
        
    def delete(self, key: bytes):
        if not self._is_open:
            raise RuntimeError("Database is closed")
        if key in self._store:
            del self._store[key]
            
    def iterator(self):
        """Returns an iterator over all keys and values in the database."""
        if not self._is_open:
            raise RuntimeError("Database is closed")
        return self._store.items()
