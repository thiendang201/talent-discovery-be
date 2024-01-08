from supabase import create_client, Client
from configs import env_configs
from constants import BUCKET_NAME

url: str = env_configs.get("SUPABASE_URL")
key: str = env_configs.get("SUPABASE_KEY")

supabase_client: Client = create_client(url, key)


def get_storage_bucket(bucket_name: str = BUCKET_NAME):
    return supabase_client.storage.from_(bucket_name)
