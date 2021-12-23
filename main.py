from src.apps import ProductApp, CustomerApp, OrderApp, LoginApp
import hydralit as hy

from src.apps.home import HomeApp


def main():
    app = hy.HydraApp(title='Sandeliapp')

    app.add_app('Home', app=HomeApp(), is_home=True)
    app.add_app("Order", app=OrderApp())
    app.add_app("Customer", app=CustomerApp())
    app.add_app('Product', app=ProductApp())

    app.add_app('Login', app=LoginApp(), is_login=True)

    app.run()


if __name__ == '__main__':
    main()
