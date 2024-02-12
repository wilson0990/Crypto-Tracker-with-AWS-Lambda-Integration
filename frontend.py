import streamlit as st
import requests

API_URL = 'http://localhost:5000'

def register(username, password, balance):
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password, "balance": balance})
    return response.json()

def login(username, password):
    response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    return response.json()

def get_prices():
    response = requests.get(f"{API_URL}/prices")
    return response.json()

def purchase(access_token, coin, quantity, price):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{API_URL}/purchase", json={"coin": coin, "quantity": quantity, "price": price}, headers=headers)
    return response.json()

def get_portfolio(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_URL}/portfolio", headers=headers)
    return response.json()

def main():
    st.title("Cryptocurrency Tracker")

    session_state = st.session_state
    if not hasattr(session_state, 'access_token'):
        session_state.access_token = None
    if not hasattr(session_state, 'page'):
        session_state.page = None

    if st.sidebar.button("Register", key="register_button"):
        session_state.page = 'register'
    if st.sidebar.button("Login", key="login_button"):
        session_state.page = 'login'

    if session_state.page == 'register':
        reg_username = st.text_input("Register Username", key="reg_username")
        reg_password = st.text_input("Register Password", type="password", key="reg_password")
        reg_balance = st.number_input("Balance", value=0.0, step=1.0, key="reg_balance")  # Unique key for each widget

        if st.button("Register", key="register_submit"):
            reg_result = register(reg_username, reg_password, reg_balance)
            st.success(reg_result.get('message'))

    elif session_state.page == 'login':
        login_username = st.text_input("Login Username", key="login_username")
        login_password = st.text_input("Login Password", type="password", key="login_password")

        if st.button("Login", key="login_submit"):
            login_result = login(login_username, login_password)
            if "access_token" in login_result:
                session_state.access_token = login_result["access_token"]
                st.success("Login successful")
                session_state.page = 'dashboard'

    if session_state.page == 'dashboard':
        prices = get_prices()
        st.header("Current Cryptocurrency Prices")
        for crypto, data in prices.items():
            if 'usd' in data:
                st.write(f"{crypto.capitalize()}: ${data['usd']}")
            else:
                st.write(f"{crypto.capitalize()}: Price data not available")

        purchase_coin = st.selectbox("Select Coin", ["bitcoin", "ethereum", "litecoin"], key="purchase_coin")
        purchase_quantity = st.number_input("Quantity", value=0.0, step=0.01, key="purchase_quantity")
        purchase_price = st.number_input("Price", value=0.0, step=0.01, key="purchase_price")  # Unique key for each widget
        if st.button("Purchase", key="purchase_submit"):
            purchase_result = purchase(session_state.access_token, purchase_coin, purchase_quantity, purchase_price)
            st.success(purchase_result.get('message'))

        portfolio = get_portfolio(session_state.access_token)
        st.header("Your Portfolio")
        for coin, quantity in portfolio.get('portfolio', {}).items():
            st.write(f"{coin.capitalize()}: {quantity}")

if __name__ == '__main__':
    main()
