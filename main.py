from src.io.loader import preload_data
from src.apps import ProductApp, CustomerApp, OrderApp, LoginApp
from src.config import DATASOURCES
import hydralit as hy
import streamlit as st
from src.apps.home import HomeApp


def main():
    app = hy.HydraApp(title='Sandeliapp')

    st.session_state.entity_dataloader = preload_data(DATASOURCES)

    app.add_app('Home', app=HomeApp(), is_home=True)
    app.add_app("Order", app=OrderApp(
        entity_dataloader=st.session_state.entity_dataloader))
    app.add_app("Customer", app=CustomerApp(
        entity_dataloader=st.session_state.entity_dataloader))
    app.add_app('Product', app=ProductApp())

    # Other pages have to be initialized before login, for redirecting after
    app.add_app('Login', app=LoginApp(),
                # is_login=True  # disable while developing
                )

    app.run()


if __name__ == '__main__':
    main()
