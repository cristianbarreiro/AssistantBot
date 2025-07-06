import os
import gradio as gr
from dotenv import load_dotenv
from ai21 import AI21Client
from ai21.models.chat import ChatMessage, ResponseFormat

load_dotenv()  # carga variables de entorno desde .env

AI21_API_KEY = os.getenv("AI21_API_KEY")
client = AI21Client(api_key=AI21_API_KEY)

FAQ = {
    "¿Cómo restablezco mi contraseña?":
        "Para restablecer tu contraseña, hacé clic en 'Olvidé mi contraseña' en el login y seguí el correo que recibís.",
    "¿Cómo cambio mi plan de suscripción?":
        "Ingresá a Configuración → Suscripción y seleccioná el plan que quieras.",
    "¿Dónde veo mi historial de pedidos?":
        "En tu perfil, dentro de 'Mis pedidos', vas a ver todos tus pedidos con estado y fecha.",
    "¿Cómo contacto al equipo de soporte?":
        "Escribinos a soporte@tusitio.com o pulsá el botón de chat en vivo abajo a la derecha.",
}

faq_list = list(FAQ.items())

def menu_preguntas():
    return (
        "Perfecto. Estas son las preguntas frecuentes:\n\n" +
        "\n".join([f"{i+1}. {q}" for i, (q, _) in enumerate(faq_list)]) +
        "\n5. Hablar con soporte AI\n\n👉 Escribí el número de la pregunta o escribí tu consulta:"
    )

def ai21_responder(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="jamba-large-1.7",  # modelo oficial para chat AI21
            messages=[ChatMessage(role="user", content=prompt)],
            max_tokens=150,
            temperature=0.7,
            response_format=ResponseFormat(type="text")
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al contactar AI21: {e}"

def responder(mensaje: str, historial: list[list[str]], stage: int):
    historial = historial or []

    # stage 1: saludo → mostrar menú
    if stage == 1:
        respuesta = menu_preguntas()
        historial.append([mensaje, respuesta])
        return historial, "", historial, 2

    # stage 2: menú, esperar selección o consulta
    if stage == 2:
        # si elige opción 5 → activar modo soporte AI (stage 3)
        if mensaje.strip() == "5":
            respuesta = "Has entrado al soporte AI. Escribí lo que quieras y te responderé. Para salir, escribí 'salir'."
            historial.append([mensaje, respuesta])
            return historial, "", historial, 3

        # procesar opciones 1-4 FAQ
        try:
            numero = int(mensaje)
            if 1 <= numero <= len(faq_list):
                pregunta, respuesta_faq = faq_list[numero - 1]
                respuesta = f"📌 {pregunta}\n\n{respuesta_faq}\n\n" + menu_preguntas()
                historial.append([mensaje, respuesta])
                return historial, "", historial, 2
        except ValueError:
            pass

        # si pregunta exacta en FAQ
        if mensaje in FAQ:
            respuesta = FAQ[mensaje] + "\n\n" + menu_preguntas()
        else:
            # pregunta libre fuera del FAQ → responder con AI y mostrar menú
            respuesta_ai = ai21_responder(mensaje)
            respuesta = f"{respuesta_ai}\n\n" + menu_preguntas()

        historial.append([mensaje, respuesta])
        return historial, "", historial, 2

    # stage 3: modo soporte AI - chat libre con IA
    if stage == 3:
        if mensaje.strip().lower() == "salir":
            respuesta = "Saliste del soporte AI. Volviendo al menú principal.\n\n" + menu_preguntas()
            historial.append([mensaje, respuesta])
            return historial, "", historial, 2

        respuesta_ai = ai21_responder(mensaje)
        historial.append([mensaje, respuesta_ai])
        return historial, "", historial, 3

def reiniciar():
    historial = [
        ["", "¡Hola!"]
    ]
    return historial, "", [], 1

with gr.Blocks() as demo:
    gr.Markdown("## 🛠️ Chatbot de Soporte\nPreguntá sobre nuestra plataforma y recibí ayuda al instante.")

    chatbot      = gr.Chatbot(label="Soporte", height=400)
    caja         = gr.Textbox(placeholder="Escribí tu mensaje...", show_label=False)
    enviar       = gr.Button("Enviar")
    reset        = gr.Button("🗑 Reiniciar chat", variant="secondary")
    estado_hist  = gr.State([])
    estado_stage = gr.State(1)

    enviar.click(responder, inputs=[caja, estado_hist, estado_stage],
                 outputs=[chatbot, caja, estado_hist, estado_stage])
    caja.submit(responder, inputs=[caja, estado_hist, estado_stage],
                outputs=[chatbot, caja, estado_hist, estado_stage])
    reset.click(fn=reiniciar, inputs=[], outputs=[chatbot, caja, estado_hist, estado_stage])
    demo.load(fn=reiniciar, inputs=[], outputs=[chatbot, caja, estado_hist, estado_stage])

demo.launch()

