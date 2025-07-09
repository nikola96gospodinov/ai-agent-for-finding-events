from typing import Optional
from datetime import datetime, date
from supabase import Client

class UserRunService:
    """Service for handling user run operations"""
    
    def __init__(self, supabase_client: Optional[Client] = None):
        self.client = supabase_client
        self.MAX_RUNS_PER_MONTH = 2
    
    def set_client(self, client: Client):
        """Set the Supabase client"""
        self.client = client
    
    async def check_user_run_limit(self, user_id: str) -> bool:
        """Check if user has exceeded their monthly run limit (max 2 runs per calendar month)"""
        if not self.client:
            print("Supabase client not initialized")
            return False
            
        try:
            # Get current date
            current_date = date.today()
            current_month = current_date.month
            current_year = current_date.year
            
            # Query runs table for the current month
            response = self.client.table('runs').select('*').eq('user_id', user_id).execute()
            
            if response.data:
                # Count runs in the current month
                current_month_runs = 0
                for run in response.data:
                    run_date_str = run.get('run_date')
                    if run_date_str:
                        try:
                            # Parse the run_date (assuming it's in ISO format)
                            run_date = datetime.fromisoformat(run_date_str.replace('Z', '+00:00')).date()
                            if run_date.month == current_month and run_date.year == current_year:
                                current_month_runs += 1
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing run_date: {e}")
                            continue
                
                # Check if user has exceeded the limit
                if current_month_runs >= self.MAX_RUNS_PER_MONTH:
                    print(f"User {user_id} has already run {current_month_runs} times this month (limit: {self.MAX_RUNS_PER_MONTH})")
                    return False
                else:
                    print(f"User {user_id} has {current_month_runs} runs this month, can run {self.MAX_RUNS_PER_MONTH - current_month_runs} more times")
                    return True
            else:
                # No runs found, user can run
                print(f"User {user_id} has no previous runs, can run up to {self.MAX_RUNS_PER_MONTH} times this month")
                return True
                
        except Exception as e:
            print(f"Error checking user run limit: {e}")
            return False
    
    async def record_user_run(self, user_id: str) -> bool:
        """Record a new run for the user"""
        if not self.client:
            print("Supabase client not initialized")
            return False
            
        try:
            # Insert a new run record
            response = self.client.table('runs').insert({
                'user_id': user_id,
                'run_date': datetime.now().isoformat()
            }).execute()
            
            if response.data:
                print(f"Successfully recorded run for user {user_id}")
                return True
            else:
                print(f"Failed to record run for user {user_id}")
                return False
                
        except Exception as e:
            print(f"Error recording user run: {e}")
            return False

user_run_service = UserRunService() 