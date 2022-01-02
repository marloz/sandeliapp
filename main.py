from src.io.loader import preload_data
from src.apps import EntityAppTemplate, OrderApp, LoginApp
from src.config import DATASOURCES
from src.entities import Customer, Product
import hydralit as hy
import streamlit as st
from src.apps.home import HomeApp


def main():
    app = hy.HydraApp(title='Sandeliapp')

    st.session_state.entity_dataloader = preload_data(DATASOURCES)

    app.add_app('Home', app=HomeApp(), is_home=True)
    app.add_app("Order", app=OrderApp(
        dataloader=st.session_state.entity_dataloader))
    app.add_app("Customer", app=EntityAppTemplate(entity=Customer,
                                                  dataloader=st.session_state.entity_dataloader,
                                                  add_default=False))
    app.add_app('Product', app=EntityAppTemplate(entity=Product,
                                                 dataloader=st.session_state.entity_dataloader))

    # Other pages have to be initialized before login, for redirecting after
    app.add_app('Login', app=LoginApp(),
                # is_login=True  # disable while developing
                )

    app.run()


if __name__ == '__main__':
    main()
