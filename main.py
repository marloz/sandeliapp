
import streamlit as st

from src.interface.multipage import MultiPage
from src.interface import welcome_page, order_page

# Create an instance of the app
app = MultiPage()

# Add all your applications (pages) here
app.add_page("Welcome", welcome_page.app)
app.add_page("Order", order_page.app)

# The main app
app.run()
