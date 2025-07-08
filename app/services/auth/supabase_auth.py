from typing import Optional, Dict, Any, cast
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.core.config import settings
from app.models.user_profile_model import UserProfile
from datetime import datetime
from app.utils.address_utils import get_address_coordinates
from app.utils.date_utils import time_to_string

security = HTTPBearer()

class SupabaseAuthService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_ANON_KEY

        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            print("Supabase credentials not found in environment variables")
    
    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Supabase token"""
        if not self.client:
            print("Supabase client not initialized")
            return None
            
        try:
            # Verify the token and get user info
            user_response = self.client.auth.get_user(token)
            if user_response and user_response.user:
                return user_response.user.model_dump()
            return None
        except Exception as e:
            print(f"Error getting user from token: {e}")
            return None
    
    async def get_user_profile(self, user_id: str, user_data: Optional[Dict[str, Any]] = None) -> Optional[UserProfile]:
        """Get user profile from Supabase database"""
        if not self.client:
            print("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table('profiles').select('*').eq('user_id', user_id).execute()

            if response.data and len(response.data) > 0:
                profile_data = response.data[0]
                return self._convert_to_user_profile(profile_data, user_data)
            else:
                print(f"No profile found for user_id: {user_id}")
                return None
                
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def _convert_to_user_profile(self, profile_data: Dict[str, Any], user_data: Optional[Dict[str, Any]] = None) -> UserProfile | None:
        """Convert database profile data to UserProfile model"""
        try:
            birthday = profile_data.get('birthday')
            if isinstance(birthday, str):
                birth_date = datetime.fromisoformat(birthday)
            elif birthday and hasattr(birthday, 'date'):  # If it's a date object
                birth_date = datetime.combine(birthday, datetime.min.time())
            else:
                birth_date = datetime(1995, 1, 1)  # Default fallback
            
            weekday_start = profile_data.get('weekday_start_time')
            weekday_end = profile_data.get('weekday_end_time')
            weekend_start = profile_data.get('weekend_start_time')
            weekend_end = profile_data.get('weekend_end_time')
            
            
            acceptable_times = {
                "weekdays": {
                    "start": time_to_string(weekday_start) or "17:00",
                    "end": time_to_string(weekday_end) or "22:00"
                },
                "weekends": {
                    "start": time_to_string(weekend_start) or "8:00",
                    "end": time_to_string(weekend_end) or "23:00"
                }
            }
            
            distance_threshold = {
                "distance_threshold": profile_data.get('distance_threshold_value', 20),
                "unit": profile_data.get('distance_threshold_unit', 'miles')
            }
            
            location = get_address_coordinates(profile_data.get('postcode'))
            
            budget_value = profile_data.get('budget', 0)
            willingness_to_pay = budget_value > 0
            
            time_commitment_in_minutes = profile_data.get('time_commitment_in_minutes', 240)
            
            # Get email from user data (auth) or profile data, with fallback to empty string
            email = ""
            if user_data and user_data.get('email'):
                email = user_data.get('email')
            
            return cast(UserProfile, {
                "birth_date": birth_date,
                "gender": profile_data.get('gender', 'male'),
                "sexual_orientation": profile_data.get('sexual_orientation', 'straight'),
                "relationship_status": profile_data.get('relationship_status', 'single'),
                "willingness_to_pay": willingness_to_pay,
                "budget": budget_value,
                "willingness_for_online": profile_data.get('willingness_for_online', False),
                "acceptable_times": acceptable_times,
                "location": location,
                "distance_threshold": distance_threshold,
                "time_commitment_in_minutes": time_commitment_in_minutes,
                "interests": profile_data.get('interests', []),
                "goals": profile_data.get('goals', []),
                "occupation": profile_data.get('occupation', ''),
                "email": email
            })
        except Exception as e:
            print(f"Error converting profile data: {e}")
            return None

# Global instance
auth_service = SupabaseAuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """Dependency to get current user from bearer token"""
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)) -> UserProfile | None:
    """Dependency to get current user's profile"""
    user_id = user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    
    profile = await auth_service.get_user_profile(user_id, user)
    if not profile:
        return None
    
    return profile 