class KeyManager:
    """Manages the generation and parsing of RocksDB keys."""
    
    @staticmethod
    def generate_key(truck_id: str, window_start: int) -> bytes:
        """
        Generates a deterministic RocksDB storage key.
        Format: {truck_id}:{window_start}
        """
        return f"{truck_id}:{window_start}".encode('utf-8')
        
    @staticmethod
    def parse_key(key_bytes: bytes) -> tuple:
        """
        Parses a RocksDB storage key back into its components.
        Returns: (truck_id: str, window_start: int)
        """
        key_str = key_bytes.decode('utf-8')
        parts = key_str.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid key format: {key_str}")
        return parts[0], int(parts[1])
