from src.entities import Customer, Manager, Product
from src.io.loader import preload_data
from src.order import OrderProcessor, Order
from src.config import ENTITIES_TO_LOAD, ORDER_TYPES
import streamlit as st


def app():

    # TODO: use auth to get id - name, location, etc, can be fetched
    MANAGER_ID = 'some_email@medexy.lt'

    # Load and cache data to be used
    data_loader = preload_data(ENTITIES_TO_LOAD)

    # Print out manager
    manager = data_loader.get_single_entity_instance(
        entity=Manager, entity_identifier=MANAGER_ID
    )
    st.write(manager)

    # Date input
    order_date = st.date_input('Order date')

    # Select order type
    order_type = st.selectbox('Order type', ORDER_TYPES)

    # Select customer
    customer_list = data_loader.data['customer']['customer_name'].tolist()
    selected_customer = st.selectbox('Customer', customer_list)
    customer = data_loader.get_single_entity_instance(Customer,
                                                      entity_identifier=selected_customer,
                                                      identifier_type='name')

    # Select product
    product_list = data_loader.data['product']['product_name'].tolist()
    selected_product = st.selectbox('Select product', product_list)
    product = data_loader.get_single_entity_instance(Product,
                                                     entity_identifier=selected_product,
                                                     identifier_type='name')

    # Check inventory
    # TODO: write order history fetching and inventory calculation logic
    if st.button('Check inventory'):
        st.write(f'Inventory holds 2 {selected_product} items')

    selected_quantity = st.number_input('Enter quantity', min_value=1)
    entered_discount = st.number_input('Enter discount %', min_value=0.,
                                       max_value=100., step=10.)

    order = Order(manager=manager,
                  customer=customer,
                  order_type=order_type,
                  items=[product],
                  quantities=[selected_quantity],
                  discounts=[entered_discount],
                  order_date=order_date)

    if st.button('Add to order'):
        order_df = OrderProcessor(order).prepare_for_export()
        st.write(order_df)
