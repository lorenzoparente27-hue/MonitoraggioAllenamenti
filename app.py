from datetime import date
import json
import os
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
        scheda_selezionata = st.selectbox("Scegli Scheda", ["Tirata", "Spinta"])

    categoria_scheda = scheda_selezionata
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
        # Chiave per memorizzare la lista corrente degli esercizi del blocco nello state
        state_key_exs = f"list_exs_{nome_blocco}_{scheda_selezionata}"

        # Intestazione con "X" inclusa e input ripetizioni in 2 colonne
        c_title, c_val = st.columns([3.5, 1], vertical_alignment="center")
        with c_title:
            st.markdown(f"### {nome_blocco} X")
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

        # Inizializzazione o reset della lista esercizi nello state se cambia scheda o non esiste
        if state_key_exs not in st.session_state:
            initial_exs = []
            for i in range(default_num_ex):
                ex_name = (
                    default_list[i]
                    if default_list and i < len(default_list)
                    else opzioni_esercizi[0]
                )
                initial_exs.append(
                    {"esercizio": ex_name, "reps": 10, "kg": 0.0}
                )
            st.session_state[state_key_exs] = initial_exs

        esercizi_correnti = st.session_state[state_key_exs]

        # Intestazioni per specificare Reps e Kg
        _, _, h_reps, h_kg, _ = st.columns([0.5, 2.5, 1.5, 1.5, 0.8])
        with h_reps:
            st.caption("Reps")
        with h_kg:
            st.caption("Kg")

        esercizi_blocco_data = []
        to_remove = None

        for i, ex_item in enumerate(esercizi_correnti):
            default_index = 0
            if ex_item["esercizio"] in opzioni_esercizi:
                default_index = opzioni_esercizi.index(ex_item["esercizio"])

            # Allineamento verticale centrato per i numeri degli esercizi, input e pulsante elimina
            col_num, col_e1, col_e2, col_e3, col_del = st.columns(
                [0.5, 2.5, 1.5, 1.5, 0.8], vertical_alignment="center"
            )
            with col_num:
                st.markdown(f"**{i+1}.**")
            with col_e1:
                ex_scelto = st.selectbox(
                    f"ex_{i}",
                    options=opzioni_esercizi,
                    index=default_index,
                    key=f"ex_{nome_blocco}_{i}_{scheda_selezionata}_{ex_item.get('id', i)}",
                    label_visibility="collapsed",
                )
            with col_e2:
                reps = st.number_input(
                    "Reps",
                    min_value=0,
                    value=int(ex_item["reps"]),
                    key=f"reps_{nome_blocco}_{i}_{scheda_selezionata}_{ex_item.get('id', i)}",
                    label_visibility="collapsed",
                )
            with col_e3:
                kg = st.number_input(
                    "Kg",
                    min_value=0.0,
                    step=0.5,
                    value=float(ex_item["kg"]),
                    key=f"kg_{nome_blocco}_{i}_{scheda_selezionata}_{ex_item.get('id', i)}",
                    label_visibility="collapsed",
                )
            with col_del:
                if st.button(
                    "-",
                    key=f"del_{nome_blocco}_{i}_{scheda_selezionata}_{ex_item.get('id', i)}",
                ):
                    to_remove = i

            # Aggiorniamo i valori correnti nello state per evitare perdita dati durante il rendering
            esercizi_correnti[i] = {
                "esercizio": ex_scelto,
                "reps": int(reps),
                "kg": kg,
                "id": ex_item.get("id", i),
            }
            esercizi_blocco_data.append(
                {"esercizio": ex_scelto, "reps": int(reps), "kg": kg}
            )

        # Gestione della rimozione dell'esercizio
        if to_remove is not None:
            esercizi_correnti.pop(to_remove)
            st.session_state[state_key_exs] = esercizi_correnti
            st.rerun()

        # Pulsante per aggiungere un nuovo esercizio al blocco al volo
        if st.button(
            f"+",
            key=f"add_row_{nome_blocco}_{scheda_selezionata}",
        ):
            esercizi_correnti.append(
                {
                    "esercizio": opzioni_esercizi[0],
                    "reps": 10,
                    "kg": 0.0,
                    "id": len(esercizi_correnti) + 1000,
                }
            )
            st.session_state[state_key_exs] = esercizi_correnti
            st.rerun()

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

    # Blocco 1 (sempre visibile, con default_volte=4)
    dati_blocco1 = gestisci_blocco(
        "Blocco 1",
        default_volte=4,
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
                        st.markdown(
                            f"**{b_name} (X{b_data['volte_ripetuto']})**"
                        )
                        for ex in b_data["esercizi"]:
                            st.markdown(
                                f"&nbsp;&nbsp;&nbsp;&nbsp;• {ex['esercizio']}:"
                                f" {ex['reps']} reps x {ex['kg']} kg"
                            )

                # Mostra le note se presenti nello storico
                if w.get("note"):
                    st.markdown("---")
                    st.markdown(f"**Note:** {w['note']}")