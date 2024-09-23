import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Configura tu archivo de credenciales de servicio
SERVICE_ACCOUNT_FILE = 'ruta/a/tu/credencial.json'  # Reemplaza con la ruta a tu archivo JSON
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/spreadsheets']

def authenticate_google_service():
    """Autenticar y crear el servicio de Google Calendar usando credenciales de servicio."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds)

def create_calendar_event(start_time_str, end_time_str, event_title, event_description):
    """Crear un evento en Google Calendar."""
    service, _ = authenticate_google_service()
    event = {
        'summary': event_title,
        'description': event_description,
        'start': {
            'dateTime': start_time_str,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': end_time_str,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

def add_reservation_to_sheet(name, date, time, duration, description, link):
    """Agregar reserva a Google Sheets."""
    _, service = authenticate_google_service()
    sheet_id = 'TU_SHEET_ID'  # Reemplaza con el ID de tu hoja de cálculo
    range_name = 'Reservas!A1'  # Cambia el rango según tu hoja

    values = [[name, date, time, duration, description, link]]
    body = {
        'values': values
    }
    
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

# Interfaz de usuario de Streamlit
st.title("Sistema de Reservas")
event_title = st.text_input("Título del evento:")
event_description = st.text_area("Descripción del evento:")
event_date = st.date_input("Fecha de la reserva:")
event_time = st.time_input("Hora de inicio:")
event_duration = st.number_input("Duración (en minutos):", min_value=1)

if st.button("Crear Reserva"):
    start_time_str = f"{event_date}T{event_time.hour}:{event_time.minute}:00"
    end_time_str = f"{event_date}T{event_time.hour}:{event_time.minute + event_duration}:00"
    
    # Crear el evento en Google Calendar
    event = create_calendar_event(start_time_str, end_time_str, event_title, event_description)
    
    # Agregar la reserva a Google Sheets
    add_reservation_to_sheet('Nombre del usuario', str(event_date), str(event_time), event_duration, event_description, event.get('htmlLink'))

    st.success("Reserva creada exitosamente!")
