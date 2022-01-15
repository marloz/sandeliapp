import time
from typing import Dict
import streamlit as st
from hydralit import HydraHeadApp


class LoginApp(HydraHeadApp):
    """
    This is an example login application to be used to secure access within a HydraApp streamlit application.
    This application implementation uses the allow_access session variable and uses the do_redirect method if the login check is successful.

    """

    def __init__(self, title='', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        """
        Application entry point.
        """

        st.markdown(
            "<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)

        _, column = st.columns([2, 2])

        form_data = self._create_login_form(column)

        pretty_btn = """
        <style>
        div[class="row-widget stButton"] > button {
            width: 100%;
        }
        </style>
        <br><br>
        """
        column.markdown(pretty_btn, unsafe_allow_html=True)

        if form_data['submitted']:
            self._do_login(form_data, column)

    def _create_login_form(self, parent_container) -> Dict:

        login_form = parent_container.form(key="login_form")

        form_state = {}
        form_state['username'] = login_form.text_input('Username')
        form_state['password'] = login_form.text_input(
            'Password', type="password")
        form_state['submitted'] = login_form.form_submit_button('Login')

        parent_container.write("sample login -> joe & joe")

        return form_state

    def _do_login(self, form_data, msg_container) -> None:

        # access_level=0 Access denied!
        access_level = self._check_login(form_data)

        if access_level > 0:
            msg_container.success(f"✔️ Login success")
            with st.spinner("🤓 now redirecting to application...."):
                time.sleep(1)

                self.set_access(1, form_data['username'])

                # Do the kick to the home page
                self.do_redirect()
        else:
            self.session_state.allow_access = 0
            self.session_state.current_user = None

            msg_container.error(
                f"❌ Login unsuccessful, 😕 please check your username and password and try again.")

    def _check_login(self, login_data) -> int:
        # this method returns a value indicating the success of verifying the login details provided and the permission level, 1 for default access, 0 no access etc.

        if login_data['username'] == 'joe' and login_data['password'] == 'joe':
            return 1
        else:
            return 0
