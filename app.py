import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
import json

# Inicializar Firebase usando secrets (recomendado para nuvem)
if not firebase_admin._apps:
    try:
        firebase_json = json.loads(st.secrets["FIREBASE_CONFIG"])
        cred = credentials.Certificate(firebase_json)
    except:
        # Para uso local com arquivo firebase_config.json
        cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Função para calcular a taxa efetiva mensal (TIR)
def calcular_taxa_efetiva(valor_veiculo, entrada, parcelas, valor_parcela):
    fluxo = [- (valor_veiculo - entrada)] + [valor_parcela] * parcelas
    tir_mensal = np.irr(fluxo)
    return round(tir_mensal * 100, 4) if tir_mensal else 0.0

# UI do Streamlit
st.title("🚗 Calculadora de Financiamento de Veículos")

st.header("📋 Preencha os dados do financiamento")

valor_veiculo = st.number_input("Valor do veículo (R$)", min_value=0.0, step=1000.0, format="%.2f")
entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, step=1000.0, format="%.2f")
parcelas = st.number_input("Número de parcelas", min_value=1, step=1)
valor_parcela = st.number_input("Valor da parcela (R$)", min_value=0.0, step=100.0, format="%.2f")

if st.button("Calcular Taxa Efetiva"):
    if valor_veiculo > 0 and entrada < valor_veiculo and parcelas > 0 and valor_parcela > 0:
        taxa = calcular_taxa_efetiva(valor_veiculo, entrada, parcelas, valor_parcela)
        st.success(f"💰 Taxa efetiva mensal estimada: **{taxa}%**")

        # Salvar no Firebase
        db.collection("financiamentos").add({
            "valor_veiculo": valor_veiculo,
            "entrada": entrada,
            "parcelas": parcelas,
            "valor_parcela": valor_parcela,
            "taxa_calculada": taxa
        })

        st.info("✅ Dados salvos no Firebase com sucesso!")
    else:
        st.warning("⚠️ Verifique se todos os dados foram preenchidos corretamente.")

st.markdown("---")
st.subheader("📄 Registros anteriores salvos no Firebase:")

# Mostrar registros salvos
try:
    docs = db.collection("financiamentos").stream()
    for doc in docs:
        dados = doc.to_dict()
        st.write(
            f"**Veículo:** R${dados['valor_veiculo']} | "
            f"Entrada: R${dados['entrada']} | "
            f"{dados['parcelas']}x R${dados['valor_parcela']} | "
            f"**Taxa:** {dados['taxa_calculada']}%"
        )
except:
    st.warning("Não foi possível acessar os dados do Firebase.")
