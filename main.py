from src.apps import EntityApp, DiscountApp, OrderApp
from src.apps.utils import get_entity_from_df, get_entity_identifier_column
from src.entities import Customer, Discount, Manager, Orders, Product, AccessLevel
from src.database.tables import ManagerTable, CustomerTable, ProductTable, DiscountTable, \
    OrdersTable
from src.database.loader import preload_data
import hydralit as hy
import streamlit as st

# MANAGER_ID = 'some_email@medexy.lt'  # for admin
# MANAGER_ID = '5f4ccfd7-7'  # for manager
MANAGER_ID = 'a69a99cc-7'  # for user


def main():
    app = hy.HydraApp(title='Sandeliapp')

    tables = [ManagerTable(), CustomerTable(), ProductTable(),
              DiscountTable(), OrdersTable()]
    st.session_state.dataloader = preload_data(tables)

    # app.add_app('Home', app=HomeApp(), is_home=True)

    # TODO: this is set in login page
    st.session_state.current_user = MANAGER_ID
    manager = get_entity_from_df(
        entity_type=Manager,
        df=st.session_state.dataloader.data[Manager.name()],
        entity_identifier_column=get_entity_identifier_column(
            Manager, 'id'),
        entity_identifier=st.session_state.current_user)
    st.session_state.current_user_access = manager.access.value

    order_app = OrderApp(entity_type=Orders,
                         dataloader=st.session_state.dataloader)
    app.add_app("Order", app=order_app)

    entity_app = EntityApp(entity_type=Customer,
                           dataloader=st.session_state.dataloader)
    app.add_app("Customer", app=entity_app)

    product_app = EntityApp(entity_type=Product,
                            dataloader=st.session_state.dataloader)
    app.add_app('Product', app=product_app)

    if st.session_state.current_user_access != AccessLevel.user.value:
        discount_app = DiscountApp(
            entity_type=Discount, dataloader=st.session_state.dataloader)
        app.add_app('Discounts', app=discount_app)

    if st.session_state.current_user_access == AccessLevel.admin.value:
        manager_app = EntityApp(entity_type=Manager,
                                dataloader=st.session_state.dataloader)
        app.add_app('Manager', app=manager_app)

    # Other pages have to be initialized before login, for redirecting after
    # app.add_app('Login', app=LoginApp(),
    #             # is_login=True  # disable while developing
    #             )

    app.run()


if __name__ == '__main__':
    main()
