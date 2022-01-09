from src.apps import EntityApp
# OrderApp, LoginApp, DiscountApp
from src.entities import Customer, Product
from src.database.tables import ManagerTable, CustomerTable, ProductTable, DiscountTable, OrdersTable
from src.database.loader import preload_data
import hydralit as hy
import streamlit as st
from src.apps.home import HomeApp


def main():
    app = hy.HydraApp(title='Sandeliapp')

    tables = [ManagerTable(), CustomerTable(), ProductTable(),
              DiscountTable(), OrdersTable()]
    st.session_state.dataloader = preload_data(tables)

    # app.add_app('Home', app=HomeApp(), is_home=True)
    # app.add_app("Order", app=OrderApp(
    #     dataloader=st.session_state.entity_dataloader))
    entity_app = EntityApp(entity_type=Customer,
                           dataloader=st.session_state.dataloader)
    app.add_app("Customer", app=entity_app)
    # app.add_app('Product', app=EntityAppTemplate(entity=Product,
    #                                              dataloader=st.session_state.entity_dataloader))
    # app.add_app('Discounts', app=DiscountApp(
    #     product_dataloader=st.session_state.entity_dataloader))

    # Other pages have to be initialized before login, for redirecting after
    # app.add_app('Login', app=LoginApp(),
    #             # is_login=True  # disable while developing
    #             )

    app.run()


if __name__ == '__main__':
    main()
