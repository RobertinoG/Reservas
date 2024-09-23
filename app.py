import streamlit as st
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

# Scopes para Google Calendar y Google Sheets
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/spreadsheets']

def authenticate_google():
    """Autenticación con Google y manejo de tokens"""
    creds = None
    # Verificar si ya tenemos credenciales guardadas (token.json)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no hay credenciales válidas, solicitar al usuario
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar las credenciales en token.json para futuras ejecuciones
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_calendar_events():
    """Obtener próximos eventos de Google Calendar"""
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # Fecha y hora actual en formato ISO
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def create_calendar_event(start_time_str, end_time_str, summary, description=''):
    """Crear un evento en Google Calendar"""
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'description': description,
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

# Interfaz en Streamlit
st.title("Aplicación de Reservas")

st.write("Aquí puedes consultar la disponibilidad o realizar una reserva.")

# Sección para mostrar eventos del calendario
st.header("Ver próximas reservas")

if st.button('Mostrar próximas 10 reservas'):
    events = get_calendar_events()
    if not events:
        st.write("No hay eventos próximos.")
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            st.write(f"{event['summary']} - {start}")

# Sección para crear una reserva nueva
st.header("Reservar una cita")

with st.form("form_reserva"):
    event_title = st.text_input('Título de la reserva', '')
    event_description = st.text_area('Descripción', '')
    event_date = st.date_input("Fecha de la reserva", datetime.date.today())
    event_time = st.time_input('Hora de la reserva', datetime.datetime.now().time())
    event_duration = st.number_input('Duración de la reserva (en horas)', min_value=1, max_value=12, step=1)
    
    submitted = st.form_submit_button("Reservar")
    
    if submitted and event_title:
        start_datetime = datetime.datetime.combine(event_date, event_time)
        end_datetime = start_datetime + datetime.timedelta(hours=event_duration)
        start_time_str = start_datetime.isoformat()
        end_time_str = end_datetime.isoformat()

        event = create_calendar_event(start_time_str, end_time_str, event_title, event_description)
        st.write(f"Reserva creada: {event.get('htmlLink')}")

st.write("Fin de la aplicación de reservas")
