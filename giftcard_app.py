import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def get_token(username, password):
    res = requests.post(f"{API_URL}/auth/authorize", json={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["access_token"]
    return None

def create_giftcard(token, number, balance):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"number": number, "balance": balance, "state": "ACTIVE"}
    return requests.post(f"{API_URL}/giftcards", json=data, headers=headers)

def list_giftcards(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/giftcards", headers=headers)

def create_monedero(token, name, total):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "totalAmount": total, "availableAmount": total}
    return requests.post(f"{API_URL}/monederos", json=data, headers=headers)

def list_monederos(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{API_URL}/monederos", headers=headers)

def transfer(token, amount, source, destination):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount": amount, "source": source, "destination": destination}
    return requests.post(f"{API_URL}/transfer", json=data, headers=headers)

st.set_page_config(page_title="Simulación API Monedero & GiftCard", layout="centered")
st.title("🎮 Demo Visual de API de Monedero y GiftCard")

if "token" not in st.session_state:
    st.session_state.token = None

with st.sidebar:
    st.header("🔐 Autenticación")
    username = st.text_input("Usuario", value="loyalty")
    password = st.text_input("Contraseña", type="password", value="loyalty")
    if st.button("Login"):
        token = get_token(username, password)
        if token:
            st.session_state.token = token
            st.success("Autenticado exitosamente")
        else:
            st.error("Credenciales inválidas")

if st.session_state.token:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎁 GiftCards", "💰 Monederos", "🔁 Transferencia", "📋 Listar GiftCards", "📦 Listar Monederos"])

    with tab1:
        st.subheader("Crear GiftCard")
        number = st.text_input("Número de GiftCard", value="GC001")
        balance = st.number_input("Saldo inicial", min_value=1, value=100)
        if st.button("Crear GiftCard"):
            r = create_giftcard(st.session_state.token, number, balance)
            if r.status_code == 200:
                st.success("GiftCard creada")
                st.json(r.json())
            else:
                st.error(f"Error: {r.text}")

    with tab2:
        st.subheader("Crear Monedero")
        name = st.text_input("Nombre del Monedero", value="miMonedero")
        amount = st.number_input("Saldo total", min_value=1, value=1000)
        if st.button("Crear Monedero"):
            r = create_monedero(st.session_state.token, name, amount)
            if r.status_code == 200:
                st.success("Monedero creado")
                st.json(r.json())
            else:
                st.error(f"Error: {r.text}")

    with tab3:
        st.subheader("Transferencia de Saldo")
        source = st.text_input("Origen (nombre o número)")
        destination = st.text_input("Destino (nombre o número)")
        amount = st.number_input("Monto a transferir", min_value=1, value=10)
        if st.button("Transferir"):
            r = transfer(st.session_state.token, amount, source, destination)
            if r.status_code == 200:
                st.success("Transferencia exitosa")
                st.json(r.json())
            else:
                st.error(f"Error: {r.text}")

    with tab4:
        st.subheader("GiftCards existentes")
        r = list_giftcards(st.session_state.token)
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.error(f"Error al obtener giftcards: {r.text}")

    with tab5:
        st.subheader("Monederos existentes")
        r = list_monederos(st.session_state.token)
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.error(f"Error al obtener monederos: {r.text}")
