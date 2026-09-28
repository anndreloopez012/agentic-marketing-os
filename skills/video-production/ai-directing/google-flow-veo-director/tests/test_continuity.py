"""Unit tests for multi-shot continuity engine."""

import unittest
from flow_veo_director.continuity import FlowSequence, FlowShot


class TestContinuity(unittest.TestCase):

    def test_flow_continuity_valid(self):
        seq = FlowSequence(
            title="Escalabilidad Cloud",
            total_seconds=20,
            concept="Demostración de despliegue de microservicios"
        )

        shot1 = FlowShot(
            take_number=1,
            start_second=0,
            end_second=10,
            start_keyframe="/assets/character_intro.jpg",
            end_keyframe_goal="Personaje señalando la pantalla a la derecha",
            character_anchor="/assets/character_master.jpg",
            action_description="Introduction to cloud dashboard",
            camera_movement="dolly_in",
            framing="medium_shot",
            lighting="corporate_volumetric",
            render_style="pixar_dreamworks_3d",
            transition_connector="match_cut_movement",
            voiceover_text="Modernizar tu infraestructura digital reduce costos operativos y elimina caídas de sistema en momentos críticos de venta."
        )

        shot2 = FlowShot(
            take_number=2,
            start_second=10,
            end_second=20,
            start_keyframe="Último fotograma de Toma 01 (at 00:10)",
            end_keyframe_goal="Primer plano con telemetría en verde",
            character_anchor="/assets/character_master.jpg",
            action_description="Showing positive metrics and latency drop",
            camera_movement="orbit_arc",
            framing="close_up",
            lighting="corporate_volumetric",
            render_style="pixar_dreamworks_3d",
            transition_connector="direct_glance_cut",
            voiceover_text="Nuestra arquitectura distribuida responde de manera instantánea, procesando miles de transacciones por segundo con seguridad garantizada."
        )

        seq.add_shot(shot1)
        seq.add_shot(shot2)

        warnings = seq.validate_continuity()
        self.assertEqual(len(warnings), 0)

        storyboard = seq.export_full_storyboard()
        self.assertIn("TOMA 01", storyboard)
        self.assertIn("TOMA 02", storyboard)
        self.assertIn("100% VALIDADOS", storyboard)


if __name__ == "__main__":
    unittest.main()
