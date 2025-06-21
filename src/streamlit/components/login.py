import extra_streamlit_components as stx
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import structlog
from streamlit_authenticator.utilities.hasher import Hasher


logging = structlog.get_logger()


# ログインの確認
def check_login():
    with open("authenticator.yaml") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    value = stx.CookieManager(key="cookie_manager").get(cookie=config["cookie"]["name"])
    if value is None:
        st.warning("**ログインしてください**")
        st.stop()


def login_form():
    with open("authenticator.yaml") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

    login_res = authenticator.login()
    if login_res is None:
        st.stop()

    name, authentication_status, username = login_res

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if "username" not in st.session_state:
        st.session_state["username"] = username

    if st.session_state["authentication_status"]:
        st.info("ログインに成功しました")
        authenticator.logout("ログアウト", "main")

        # ここにログイン後の処理を書く。
    elif st.session_state["authentication_status"] is False:
        st.error("ユーザ名またはパスワードが間違っています")
    elif st.session_state["authentication_status"] is None:
        st.warning("ユーザ名やパスワードを入力してください")


def generate_password_hash(password: str) -> str:
    """
    パスワードハッシュを生成する

    Parameters
    ----------
    password : str
        パスワード

    Returns
    -------
    str
        パスワードハッシュ
    """
    return Hasher([password]).generate()
