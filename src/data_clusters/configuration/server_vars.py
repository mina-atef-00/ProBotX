import os
import dotenv

dotenv.load_dotenv()

ROOT_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
)
env_file = os.path.join(ROOT_PATH, ".env")


server = {
    "token": os.getenv("token"),
    "openweather_appid": os.getenv("openweather_appid"),
    "unsplash_access_key": os.getenv("unsplash_access_key"),
    "mongo_user": os.getenv("mongo_user"),
    "mongo_pass": os.getenv("mongo_pass"),
    "mongo_hostname": os.getenv("mongo_hostname"),
    "mongo_clustername": os.getenv("mongo_clustername"),
    "prefix": os.getenv("prefix"),
    "server_id": int(os.getenv("server_id")),
    "ready_chan": int(os.getenv("ready_chan")),
    "mod_chan": int(os.getenv("mod_chan")),
    "join_exit_chan": int(os.getenv("join_exit_chan")),
    "role_on_join_id": int(os.getenv("role_on_join_id")),
    "member_logs_chan": int(os.getenv("member_logs_chan")),
    "msg_logs_chan": int(os.getenv("msg_logs_chan")),
    "newbie_chan": int(os.getenv("newbie_chan")),
    "role_on_mute": int(os.getenv("role_on_mute")),
    "mod_mail_chan": int(os.getenv("mod_mail_chan")),
    "mod_mail_categ": int(os.getenv("mod_mail_categ")),
    "confessions_chan": int(os.getenv("confessions_chan")),
}
