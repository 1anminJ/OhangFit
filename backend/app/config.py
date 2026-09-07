from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경변수 기반 설정. .env 파일 또는 실제 환경변수에서 로드."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 컨테이너 밖(로컬 alembic/uvicorn)에서 docker-compose db에 붙을 때 기본값. 포트는 docker-compose.yml 참고
    database_url: str = "postgresql+psycopg://ohangfit:ohangfit@localhost:5433/ohangfit"
    # 로컬 개발 시 frontend(npm run dev) 오리진 허용
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
