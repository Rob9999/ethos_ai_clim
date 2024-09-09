import unittest
from ethos_ai.simulation.SimulationTopic import SimulationTopic
from ethos_ai.topic.aspiration_topic import AspirationTopic


class Test_SiumulationTopic(unittest.TestCase):

    def test_some_function(self):
        simulation_topic = SimulationTopic(
            description="Verbesserung der Lebensqualität durch eine neue Ernährungsstrategie",
            parameters={"strategy": "vegetarische Ernährung", "duration": "6 Monate"},
            answer="Eine vegetarische Ernährung über 6 Monate hinweg ausprobieren.",
            overall_ethic_value=7.5,
            decision="GO",
            domain_ethic_values=[2.5, 3.0, 2.0],
            summary_reason="Positive Auswirkungen auf Gesundheit und Umwelt.",
        )
        aspiration_topic = AspirationTopic.promote_to_aspiration(simulation_topic)
        print(aspiration_topic.aspiration)
        self.assertNotEqual(aspiration_topic.aspiration, None)


if __name__ == "__main__":
    unittest.main()
