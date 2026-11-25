from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from .services import consultar_ia


class ChatViewTests(TestCase):
    def test_chat_muestra_el_formulario_con_el_campo_de_consulta_y_el_boton_de_envio(
        self,
    ):
        response = self.client.get(reverse("chat"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="consulta"')
        self.assertContains(response, "Enviar")

    def test_el_aviso_de_procesamiento_esta_oculto_y_el_boton_habilitado_al_abrir_chat(
        self,
    ):
        response = self.client.get(reverse("chat"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p id="aviso-procesando" role="status" hidden>')
        self.assertContains(response, "La IA está procesando la consulta")
        self.assertContains(response, '<button type="submit">Enviar</button>')

    def test_la_pagina_con_la_respuesta_se_muestra_sin_aviso_y_con_el_formulario_habilitado(
        self,
    ):
        with patch("chat.views.consultar_ia") as consultar_ia:
            consultar_ia.return_value = "Vendiste $ 5500,00 en total."

            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vendiste $ 5500,00 en total.")
        self.assertContains(response, '<p id="aviso-procesando" role="status" hidden>')
        self.assertContains(response, '<button type="submit">Enviar</button>')

    def test_chat_carga_el_script_que_maneja_el_aviso_de_procesamiento(self):
        response = self.client.get(reverse("chat"))

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode(),
            r'<script src="[^"]*chat/js/chat\.js" defer></script>',
        )

    def test_enviar_una_consulta_muestra_la_respuesta_de_la_ia_en_la_misma_pagina(
        self,
    ):
        with patch("chat.views.consultar_ia") as consultar_ia:
            consultar_ia.return_value = "Vendiste $ 5500,00 en total."

            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )

        self.assertEqual(response.status_code, 200)
        consultar_ia.assert_called_once_with("¿Cuánto vendí en total?", [])
        self.assertContains(response, "Vendiste $ 5500,00 en total.")
        self.assertContains(response, 'name="consulta"')

    def test_el_hilo_anterior_se_muestra_en_orden_al_volver_a_chat(self):
        with patch("chat.views.consultar_ia") as consultar_ia:
            consultar_ia.side_effect = [
                "Vendiste $ 5500,00 en total.",
                "Tu producto más vendido es Café molido.",
            ]

            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )
            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuál fue mi producto más vendido?"},
            )

        response = self.client.get(reverse("chat"))

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        intercambios = [
            "¿Cuánto vendí en total?",
            "Vendiste $ 5500,00 en total.",
            "¿Cuál fue mi producto más vendido?",
            "Tu producto más vendido es Café molido.",
        ]
        for texto in intercambios:
            self.assertIn(texto, html)
        posiciones = [html.index(texto) for texto in intercambios]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertContains(response, 'name="consulta"')

    def test_una_nueva_consulta_agrega_su_intercambio_al_final_del_hilo(self):
        with patch("chat.views.consultar_ia") as consultar_ia:
            consultar_ia.return_value = "Vendiste $ 5500,00 en total."
            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )

            consultar_ia.return_value = "Tu producto más vendido es Café molido."
            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuál fue mi producto más vendido?"},
            )

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        intercambios = [
            "¿Cuánto vendí en total?",
            "Vendiste $ 5500,00 en total.",
            "¿Cuál fue mi producto más vendido?",
            "Tu producto más vendido es Café molido.",
        ]
        for texto in intercambios:
            self.assertIn(texto, html)
        posiciones = [html.index(texto) for texto in intercambios]
        self.assertEqual(posiciones, sorted(posiciones))

    def test_consulta_vacia_muestra_el_aviso_y_no_modifica_el_hilo(self):
        with patch("chat.views.consultar_ia") as consultar_ia:
            consultar_ia.return_value = "Vendiste $ 5500,00 en total."
            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )

            response = self.client.post(reverse("chat"), {"consulta": "   "})

            consultar_ia.assert_called_once_with("¿Cuánto vendí en total?", [])

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Escribí una consulta")
        self.assertContains(response, "¿Cuánto vendí en total?")
        self.assertContains(response, "Vendiste $ 5500,00 en total.")

        response = self.client.get(reverse("chat"))
        html = response.content.decode()
        self.assertEqual(html.count("Vos:"), 1)
        self.assertEqual(html.count("IA:"), 1)
        self.assertEqual(html.count("¿Cuánto vendí en total?"), 1)
        self.assertEqual(html.count("Vendiste $ 5500,00 en total."), 1)

    def test_consulta_vacia_no_consulta_a_la_ia_y_muestra_un_mensaje_de_validacion(
        self,
    ):
        for consulta in ("", "   "):
            with patch("chat.views.consultar_ia") as consultar_ia:
                response = self.client.post(
                    reverse("chat"),
                    {"consulta": consulta},
                )

            self.assertEqual(response.status_code, 200)
            consultar_ia.assert_not_called()
            self.assertContains(response, "Escribí una consulta")
            self.assertContains(response, 'name="consulta"')

    def test_una_pregunta_de_seguimiento_se_envia_a_la_ia_con_el_intercambio_anterior(
        self,
    ):
        with patch("chat.services.subprocess.run") as run:
            run.side_effect = [
                Mock(stdout="Vendiste $ 5500,00 en total.\n"),
                Mock(stdout="En enero vendiste $ 4200,00.\n"),
            ]

            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )
            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Y en enero?"},
            )

        self.assertEqual(response.status_code, 200)
        comando = run.call_args.args[0]
        self.assertEqual(
            comando[-1],
            (
                "Conversación previa:\n"
                "Vos: ¿Cuánto vendí en total?\n"
                "IA: Vendiste $ 5500,00 en total.\n"
                "\n"
                "Consulta actual: ¿Y en enero?"
            ),
        )

    def test_un_seguimiento_con_varios_intercambios_se_envia_a_la_ia_con_todo_el_hilo(
        self,
    ):
        with patch("chat.services.subprocess.run") as run:
            run.side_effect = [
                Mock(stdout="Vendiste $ 5500,00 en total.\n"),
                Mock(stdout="Tu producto más vendido es Café molido.\n"),
                Mock(stdout="En enero vendiste $ 4200,00.\n"),
            ]

            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )
            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuál fue mi producto más vendido?"},
            )
            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Y en enero?"},
            )

        self.assertEqual(response.status_code, 200)
        comando = run.call_args.args[0]
        self.assertEqual(
            comando[-1],
            (
                "Conversación previa:\n"
                "Vos: ¿Cuánto vendí en total?\n"
                "IA: Vendiste $ 5500,00 en total.\n"
                "Vos: ¿Cuál fue mi producto más vendido?\n"
                "IA: Tu producto más vendido es Café molido.\n"
                "\n"
                "Consulta actual: ¿Y en enero?"
            ),
        )

    def test_un_seguimiento_despues_de_volver_a_chat_se_envia_a_la_ia_con_el_hilo_anterior(
        self,
    ):
        with patch("chat.services.subprocess.run") as run:
            run.side_effect = [
                Mock(stdout="Vendiste $ 5500,00 en total.\n"),
                Mock(stdout="En enero vendiste $ 4200,00.\n"),
            ]

            self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )
            respuesta_anterior = self.client.get(reverse("chat"))
            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Y en enero?"},
            )

        self.assertContains(respuesta_anterior, "Vendiste $ 5500,00 en total.")
        self.assertEqual(response.status_code, 200)
        comando = run.call_args.args[0]
        self.assertEqual(
            comando[-1],
            (
                "Conversación previa:\n"
                "Vos: ¿Cuánto vendí en total?\n"
                "IA: Vendiste $ 5500,00 en total.\n"
                "\n"
                "Consulta actual: ¿Y en enero?"
            ),
        )

    def test_la_primera_consulta_se_envia_a_la_ia_sin_contexto_previo(self):
        with patch("chat.services.subprocess.run") as run:
            run.return_value.stdout = "Vendiste $ 5500,00 en total.\n"

            response = self.client.post(
                reverse("chat"),
                {"consulta": "¿Cuánto vendí en total?"},
            )

        self.assertEqual(response.status_code, 200)
        comando = run.call_args.args[0]
        self.assertEqual(comando[-1], "¿Cuánto vendí en total?")


class ConsultarIATests(TestCase):
    def test_la_consulta_ejecuta_opencode_en_el_directorio_del_proyecto(
        self,
    ):
        with patch("chat.services.subprocess.run") as run:
            run.return_value.stdout = "Vendiste $ 5500,00 en total.\n"

            respuesta = consultar_ia("¿Cuánto vendí?")

        run.assert_called_once_with(
            [
                "opencode",
                "run",
                "--model",
                "opencode/deepseek-v4.1-flash-free",
                "¿Cuánto vendí?",
            ],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(respuesta, "Vendiste $ 5500,00 en total.")
