"""Test suite for Kafka relay settings."""

from template.settings.kafka_settings import KafkaSettings


class TestKafkaSettings:
    """Test cases for Kafka environment configuration."""

    def test_loads_defaults(self):
        """
        GIVEN no Kafka environment overrides
        WHEN settings are loaded
        THEN local relay defaults are available
        """
        # WHEN
        settings = KafkaSettings()

        # THEN
        assert settings.BOOTSTRAP_SERVERS == "localhost:9092"
        assert settings.USER_EVENTS_TOPIC == "users.events"
