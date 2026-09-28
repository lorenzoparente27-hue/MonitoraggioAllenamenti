from datetime import date, datetime, timedelta
import json
import os
import calendar
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

    def gestisci_blocco(
        nome_blocco,
        default_volte=2,
        nascondi_se_zero=False,
        default_num_ex=4,
        default_list=None,
    ):
        state_key_exs = f"list_exs_{nome_blocco}_{scheda_selezionata}"

        c_title, c_val = st.columns([3.5, 1], vertical_alignment="center")
        with c_title:
            st.markdown(f"### {nome_blocco}")
        with c_val:
            ripetizioni_blocco = st.number_input(
                "volte",
                min_value=0,
                max_value=10,
                value=default_volte,
                key=f"rep_{nome_blocco}_{scheda_selezionata}",
                label_visibility="collapsed",
            )

        if nascondi_se_zero and ripetizioni_blocco == 0:
            return {"volte_ripetuto": 0, "esercizi": []}

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

            esercizi_correnti[i] = {
                "esercizio": ex_scelto,
                "reps": int(reps),
                "kg": kg,
                "id": ex_item.get("id", i),
            }
            esercizi_blocco_data.append(
                {"esercizio": ex_scelto, "reps": int(reps), "kg": kg}
            )

        if to_remove is not None:
            esercizi_correnti.pop(to_remove)
            st.session_state[state_key_exs] = esercizi_correnti
            st.rerun()

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

    dati_blocco1 = gestisci_blocco(
        "Blocco 1",
        default_volte=4,
        nascondi_se_zero=False,
        default_num_ex=5,
        default_list=default_blocco1_list,
    )

    st.divider()

    dati_blocco2 = gestisci_blocco(
        "Blocco 2", default_volte=0, nascondi_se_zero=True, default_num_ex=4
    )

    st.divider()

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
# SEZIONE 3: STORICO (Calendario Mensile)
# ---------------------------------------------------------
elif menu == "Storico":
    st.header("Calendario Allenamenti")

    if not db["workouts"]:
        st.info("Nessun allenamento registrato finora.")
    else:
        # Mappa delle date registrate per un accesso rapido
        workouts_by_date = {w["date"]: w for w in db["workouts"]}
        
        # Otteniamo la lista di tutte le date registrate in formato datetime.date
        all_workout_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in workouts_by_date.keys()]

        # Selettore di Anno e Mese per navigare nel calendario
        mesi_nomi = {
            1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
            5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
            9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
        }

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            anni_disponibili = sorted(list(set([d.year for d in all_workout_dates])), reverse=True)
            selected_year = st.selectbox("Anno", anni_disponibili)
        with col_m2:
            mesi_disponibili = sorted(list(set([d.month for d in all_workout_dates if d.year == selected_year])))
            # Se l'anno ha mesi, mostriamo quelli, altrimenti di default il mese corrente
            selected_month = st.selectbox(
                "Mese", 
                options=mesi_disponibili if mesi_disponibili else [date.today().month],
                format_func=lambda x: mesi_nomi[x]
            )

        st.markdown("---")

        # Inizializziamo la chiave nello state per la data selezionata se non esiste
        if "selected_calendar_date" not in st.session_state:
            st.session_state["selected_calendar_date"] = str(max(all_workout_dates))

        # Costruzione della griglia del calendario per il mese e anno selezionati
        cal = calendar.Calendar(firstweekday=0) # Inizia da Lunedì
        month_days = cal.monthdayscalendar(selected_year, selected_month)

        st.subheader(f"📅 {mesi_nomi[selected_month]} {selected_year}")

        # Intestazione giorni della settimana
        giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
        cols_header = st.columns(7)
        for idx, g in enumerate(giorni_settimana):
            with cols_header[idx]:
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{g}</div>", unsafe_allow_html=True)

        # Rendering della griglia del mese
        for week in month_days:
            cols_week = st.columns(7)
            for idx, day in enumerate(week):
                with cols_week[idx]:
                    if day == 0:
                        # Giorno vuoto del mese precedente/successivo
                        st.markdown("<div style='text-align: center; color: gray; padding: 10px;'>-</div>", unsafe_allow_html=True)
                    else:
                        # Creazione stringa data formattata YYYY-MM-DD
                        current_date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                        
                        if current_date_str in workouts_by_date:
                            w_info = workouts_by_date[current_date_str]
                            # Distinguiamo il colore del bottone in base al tipo di scheda (usando le emoji o i tipi di pulsante)
                            colore_etichetta = "🟢" if w_info["scheda"] == "Tirata" else "🔵"
                            
                            # Giorno con allenamento: colorato e cliccabile
                            if st.button(f"{colore_etichetta} {day}", key=f"day_{current_date_str}", use_container_width=True):
                                st.session_state["selected_calendar_date"] = current_date_str
                                st.rerun()
                        else:
                            # Giorno senza allenamento: disabilitato / non cliccabile
                            st.markdown(
                                f"<div style='text-align: center; padding: 8px; background-color: #f0f2f6; border-radius: 5px; color: #a3a3a3; margin-bottom: 5px;'>{day}</div>", 
                                unsafe_allow_html=True
                            )

        st.divider()

        # Visualizzazione dettagli allenamento del giorno selezionato nel calendario
        target_date = st.session_state["selected_calendar_date"]
        if target_date in workouts_by_date:
            w = workouts_by_date[target_date]
            st.markdown(f"### Dettaglio Allenamento del **{target_date}**")
            
            with st.container(border=True):
                st.subheader(f"🏋️ Scheda: {w['scheda']}")
                for b_name, b_data in [
                    ("Blocco 1", w.get("blocco_1")),
                    ("Blocco 2", w.get("blocco_2")),
                ]:
                    if b_data and b_data["volte_ripetuto"] > 0:
                        st.markdown(f"**{b_name} (Ripetuto {b_data['volte_ripetuto']} volte)**")
                        for ex in b_data["esercizi"]:
                            st.markdown(
                                f"&nbsp;&nbsp;&nbsp;&nbsp;• **{ex['esercizio']}**: "
                                f"{ex['reps']} reps × {ex['kg']} kg"
                            )
                
                if w.get("note"):
                    st.markdown("---")
                    st.markdown(f"**Note:** {w['note']}")
        else:
            # Seleziona di default il primo allenamento disponibile se la data non corrisponde
            primo_disponibile = list(workouts_by_date.keys())[-1]
            st.session_state["selected_calendar_date"] = primo_disponibile
            st.rerun()