import gradio as gr

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
    return "Perfecto. Estas son las preguntas frecuentes:\n\n" + \
           "\n".join([f"{i+1}. {q}" for i, (q, _) in enumerate(faq_list)]) + \
           "\n\n👉 Escribí el número de la pregunta o escribí tu consulta:"

def responder(mensaje: str, historial: list[list[str]], stage: int):
    historial = historial or []

    # Etapa 1: el usuario saluda → bot responde con menú
    if stage == 1:
        historial.append([mensaje, None])  # Usuario habla
        historial.append([None, menu_preguntas()])  # Bot responde
        return historial, "", historial, 2

    # Etapa 2+: manejar consulta como número o texto
    try:
        numero = int(mensaje)
        if 1 <= numero <= len(faq_list):
            pregunta, respuesta = faq_list[numero - 1]
            historial.append([mensaje, None])  # Usuario envía número
            historial.append([None, f"📌 {pregunta}\n\n{respuesta}"])
            historial.append([None, menu_preguntas()])
            return historial, "", historial, 2
    except ValueError:
        pass

    if mensaje in FAQ:
        respuesta = FAQ[mensaje]
    else:
        respuesta = "Lo siento, no entiendo esa pregunta. Probá con otra o contactá a soporte@tusitio.com"

    historial.append([mensaje, None])  # Usuario pregunta
    historial.append([None, respuesta])
    historial.append([None, menu_preguntas()])
    return historial, "", historial, 2

def reiniciar():
    historial = [
        [None, "¡Hola!"]
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
