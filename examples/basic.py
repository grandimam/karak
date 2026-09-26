from karak import Karak

app = Karak()


@app.get(path="/", methods=["GET"])
async def index():
    return "Hello from Karak"


@app.get(path="/users/{user_id}", methods=["GET"])
async def user(user_id: int, active: bool = True):
    return f"User {user_id} · active={active}"
