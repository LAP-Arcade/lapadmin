from app.db import AuthToken, session
from app.tasks import task


@task("interval", days=1)
def cleanup_expired_tokens():
    with session() as s:
        deleted = AuthToken.delete_expired(s)
        s.commit()
    if deleted:
        print(f"Deleted {deleted} expired auth tokens")
