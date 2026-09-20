import json
import os
from datetime import date
import pandas as pd
import streamlit as st

# File di persistenza dei dati
DB_FILE = "gym_data_v2.json"


def load_data():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  else:
    default_data = {
        "exercises": {
            "Tirata": [
                "trazioni",
                "rematore",
                "bicipiti",
                "stacchi 1 gamba",
                "stacchi 2 gambe",
                "trapezi",
            ],
            "Spinta": [
                "dip",
                "panca",
                "alzate",
                "squat",
                "affondi",
                "spinte",
            ],
        },
        "workouts": [],
    }
    save_data(default_data)
    return default_data


def save_data(data):
  with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


# Caricamento dati
db = load_data()

# Titolo principale nativo di Streamlit
st.title("MONITORAGGIO ALLENAMENTI")

# Menu di navigazione laterale
menu = st.sidebar.selectbox(
    "Navigazione", ["Registra Allenamento", "Gestione Esercizi", "Storico"]
)

# ---------------------------------------------------------
# SEZIONE 1: REGISTRA ALLENAMENTO
# ---------------------------------------------------------
if menu == "Registra Allenamento":
  st.header("Aggiungi sessione di allenamento")

  col1, col2 = st.columns(2)
  with col1:
    workout_date = st.date_input("Data Allenamento", value=date.today())
  with col2:
    scheda_selezionata = st.selectbox(
        "Scegli Scheda", ["Tirata (Scheda A)", "Spinta (Scheda B)"]
    )

  categoria_scheda = "Tirata" if "Tirata" in scheda_selezionata else "Spinta"
  opzioni_esercizi = db["exercises"][categoria_scheda]

  st.divider()


  # Funzione di supporto per rendere un blocco riutilizzabile
  def gestisci_blocco(
      nome_blocco,
      default_volte=2,
      nascondi_se_zero=False,
      default_num_ex=4,
      default_list=None,
  ):
    c_title, c_x, c_val = st.columns([3, 0.5, 1])
    with c_title:
      st.subheader(nome_blocco)
    with c_x:
      st.subheader("X")
    with c_val:
      ripetizioni_blocco = st.number_input(
          "volte",
          min_value=0,
          max_value=10,
          value=default_volte,
          key=f"rep_{nome_blocco}_{scheda_selezionata}",
          label_visibility="collapsed",
      )

    # Se è richiesto di nascondere e il valore è 0, restituiamo dati vuoti
    if nascondi_se_zero and ripetizioni_blocco == 0:
      return {"volte_ripetuto": 0, "esercizi": []}

    # Riga pulita per il numero esercizi
    c_lbl, c_num = st.columns([3, 1])
    with c_lbl:
      st.markdown("Numero esercizi")
    with c_num:
      num_esercizi = st.number_input(
          "num_ex",
          min_value=1,
          max_value=10,
          value=default_num_ex,
          key=f"num_ex_{nome_blocco}_{scheda_selezionata}",
          label_visibility="collapsed",
      )

    esercizi_blocco_data = []
    for i in range(int(num_esercizi)):
      # Imposta l'indice di default in base alla lista fornita
      default_index = i if default_list and i < len(default_list) else 0
      if default_list and i < len(default_list):
        item_cercato = default_list[i]
        if item_cercato in opzioni_esercizi:
          default_index = opzioni_esercizi.index(item_cercato)

      col_num, col_e1, col_e2, col_e3 = st.columns([0.5, 3, 1.5, 1.5])
      with col_num:
        st.markdown(f"**{i+1}.**")
      with col_e1:
        ex_scelto = st.selectbox(
            f"ex_{i}",
            options=opzioni_esercizi,
            index=default_index,
            key=f"ex_{nome_blocco}_{i}_{scheda_selezionata}",
            label_visibility="collapsed",
        )
      with col_e2:
        reps = st.number_input(
            "Reps",
            min_value=0,
            value=10,
            key=f"reps_{nome_blocco}_{i}_{scheda_selezionata}",
            label_visibility="collapsed",
        )
      with col_e3:
        kg = st.number_input(
            "Kg",
            min_value=0.0,
            step=0.5,
            value=0.0,
            key=f"kg_{nome_blocco}_{i}_{scheda_selezionata}",
            label_visibility="collapsed",
        )

      esercizi_blocco_data.append(
          {"esercizio": ex_scelto, "reps": int(reps), "kg": kg}
      )

    return {
        "volte_ripetuto": int(ripetizioni_blocco),
        "esercizi": esercizi_blocco_data,
    }


  # Imposta i default specifici del Blocco 1 in base alla scheda scelta
  if categoria_scheda == "Tirata":
    default_blocco1_list = [
        "trazioni",
        "rematore",
        "bicipiti",
        "stacchi 1 gamba",
        "stacchi 2 gambe",
    ]
  else:
    default_blocco1_list = ["dip", "panca", "alzate", "squat", "affondi"]

  # Blocco 1 (sempre visibile, con 5 esercizi di default preimpostati)
  dati_blocco1 = gestisci_blocco(
      "Blocco 1",
      default_volte=2,
      nascondi_se_zero=False,
      default_num_ex=5,
      default_list=default_blocco1_list,
  )

  st.divider()

  # Blocco 2 (se impostato a 0, gli esercizi sottostanti scompaiono)
  dati_blocco2 = gestisci_blocco(
      "Blocco 2", default_volte=0, nascondi_se_zero=True, default_num_ex=4
  )

  st.divider()

  # Campo Note facoltativo
  note_allenamento = st.text_area(
      "NOTE (facoltativo)",
      placeholder="Aggiungi annotazioni sull'allenamento, sensazioni, carichi, ecc...",
  )

  if st.button("💾 Salva Allenamento", type="primary", use_container_width=True):
    new_workout = {
        "date": str(workout_date),
        "scheda": scheda_selezionata,
        "blocco_1": dati_blocco1,
        "blocco_2": dati_blocco2,
        "note": note_allenamento,
    }
    db["workouts"].append(new_workout)
    save_data(db)
    st.success("Allenamento salvato con successo! Ottimo lavoro! 🎉")

# ---------------------------------------------------------
# SEZIONE 2: GESTIONE ESERCIZI (Banca Dati)
# ---------------------------------------------------------
elif menu == "Gestione Esercizi":
  st.header("Modifica Esercizi Disponibili")

  tab1, tab2 = st.tabs(["Tirata", "Spinta"])

  with tab1:
    st.subheader("Elenco Esercizi Tirata")
    for idx, ex in enumerate(db["exercises"]["Tirata"]):
      st.text(f"• {ex}")

    st.markdown("---")
    with st.form("add_tirata"):
      nuovo_ex_t = st.text_input("Aggiungi nuovo esercizio a Tirata")
      submitted_t = st.form_submit_button("Aggiungi")
      if submitted_t and nuovo_ex_t:
        db["exercises"]["Tirata"].append(nuovo_ex_t)
        save_data(db)
        st.success(f"Aggiunto '{nuovo_ex_t}'!")
        st.rerun()

  with tab2:
    st.subheader("Elenco Esercizi Spinta")
    for idx, ex in enumerate(db["exercises"]["Spinta"]):
      st.text(f"• {ex}")

    st.markdown("---")
    with st.form("add_spinta"):
      nuovo_ex_s = st.text_input("Aggiungi nuovo esercizio a Spinta")
      submitted_s = st.form_submit_button("Aggiungi")
      if submitted_s and nuovo_ex_s:
        db["exercises"]["Spinta"].append(nuovo_ex_s)
        save_data(db)
        st.success(f"Aggiunto '{nuovo_ex_s}'!")
        st.rerun()

# ---------------------------------------------------------
# SEZIONE 3: STORICO
# ---------------------------------------------------------
elif menu == "Storico":
  st.header("Storico Allenamenti")

  if not db["workouts"]:
    st.info("Nessun allenamento registrato finora.")
  else:
    for idx, w in enumerate(reversed(db["workouts"])):
      with st.expander(f"📅 {w['date']} — {w['scheda']}"):
        for b_name, b_data in [
            ("Blocco 1", w.get("blocco_1")),
            ("Blocco 2", w.get("blocco_2")),
        ]:
          if b_data and b_data["volte_ripetuto"] > 0:
            st.markdown(f"**{b_name} (X{b_data['volte_ripetuto']})**")
            for ex in b_data["esercizi"]:
              st.markdown(
                  f"&nbsp;&nbsp;&nbsp;&nbsp;• {ex['esercizio']}:"
                  f" {ex['reps']} reps x {ex['kg']} kg"
              )

        # Mostra le note se presenti nello storico
        if w.get("note"):
          st.markdown("---")
          st.markdown(f"**Note:** {w['note']}")