from typing import Optional
from supabase import create_client, Client
from app.core.config import settings


class SupabaseBaseClient:
    """
    Base class for Supabase client initialization and management.
    
    This class implements the Singleton pattern to ensure only one Supabase client
    instance is created and reused across the application.
    
    Usage:
        # In any service, import and use the global instance
        from app.core.supabase_client import supabase_base
        
        class MyService:
            def __init__(self):
                pass
            
            @property
            def client(self):
                return supabase_base.client
            
            def some_method(self):
                if self.client:
                    response = self.client.table('my_table').select('*').execute()
                    return response.data
    """
    
    _instance: Optional['SupabaseBaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client with configuration from settings"""
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        if self.supabase_url and self.supabase_key:
            try:
                self._client = create_client(self.supabase_url, self.supabase_key)
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
                self._client = None
        else:
            print("Supabase credentials not found in environment variables")
            self._client = None
    
    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self._client
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance (alternative method)"""
        return self._client
    
    def is_initialized(self) -> bool:
        """Check if the Supabase client is properly initialized"""
        return self._client is not None
    
    def reset_client(self):
        """Reset the client (useful for testing or reconnection)"""
        self._client = None
        self._initialize_client()


# Global instance - use this in all services
supabase_base = SupabaseBaseClient() 