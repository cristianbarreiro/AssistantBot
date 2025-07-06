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

faq_list = list(FAQ.items())  # [(pregunta, respuesta), ...]

def menu_preguntas():
    return "\n".join([f"{i+1}. {q}" for i, (q, _) in enumerate(faq_list)]) + \
        "\n\n👉 Escribí el número de la pregunta o escribí tu consulta:"

def responder(mensaje: str, historial: list[list[str]]):
    historial = historial or []

    # Intentar convertir mensaje a número
    try:
        numero = int(mensaje)
        if 1 <= numero <= len(faq_list):
            pregunta, respuesta = faq_list[numero - 1]
            historial.append(["user", f"{numero}"])  # Mostrar número que ingresó
            historial.append(["assistant", f"📌 {pregunta}\n\n{respuesta}"])
            historial.append(["assistant", "¿Querés saber algo más?\n\n" + menu_preguntas()])
            return historial, "", historial
    except ValueError:
        pass  # No es un número, sigue el flujo normal

    # Buscar pregunta exacta (por texto)
    if mensaje in FAQ:
        respuesta = FAQ[mensaje]
    else:
        respuesta = "Lo siento, no entiendo esa pregunta. Probá con otra o contactá a soporte@tusitio.com"

    historial.append(["user", mensaje])
    historial.append(["assistant", respuesta])
    historial.append(["assistant", "¿Querés saber algo más?\n\n" + menu_preguntas()])

    return historial, "", historial

def reiniciar():
    historial = [
        ["assistant", "¡Hola! ¿En qué puedo ayudarte?"],
        ["assistant", "Preguntas frecuentes:\n\n" + menu_preguntas()]
    ]
    return historial, "", []

with gr.Blocks() as demo:
    gr.Markdown("## 🛠️ Chatbot de Soporte\nPreguntá sobre nuestra plataforma y recibí ayuda al instante.")

    chatbot = gr.Chatbot(label="Soporte", height=400)
    caja = gr.Textbox(placeholder="Escribí tu pregunta o el número...", show_label=False)
    enviar = gr.Button("Enviar")
    reset = gr.Button("🗑 Reiniciar chat", variant="secondary")
    estado = gr.State([])

    enviar.click(responder, inputs=[caja, estado], outputs=[chatbot, caja, estado])
    caja.submit(responder, inputs=[caja, estado], outputs=[chatbot, caja, estado])
    reset.click(fn=reiniciar, inputs=[], outputs=[chatbot, caja, estado])
    demo.load(fn=reiniciar, inputs=[], outputs=[chatbot, caja, estado])

demo.launch()
