from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_url: str
    app_name: str = "IP5 FastAPI App"

    # When true service principal credentials are used to authenticate, when false local az login is assumed
    az_use_sp_authentication: bool = False
    az_tenant_id: str = ''
    az_client_id: str = ''
    az_client_secret: str = ''
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def is_sp_auth_possible(self):
        return self.az_use_sp_authentication and self.az_tenant_id.strip() and self.az_client_id.strip() and self.az_client_secret.strip()


settings = Settings()
