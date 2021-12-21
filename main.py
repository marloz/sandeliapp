import streamlit as st

from src.pages.multipage import MultiPage
from src.pages import welcome, order, customer, product


# Create an instance of the app
app = MultiPage()

# Add all your applications (pages) here
app.add_page("Home", welcome.app)
app.add_page("Order", order.app)
app.add_page("Customer", customer.app)
app.add_page('Product', product.app)

# The main app
app.run()
