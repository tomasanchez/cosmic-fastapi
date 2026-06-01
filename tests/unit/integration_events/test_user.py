"""Test suite for user integration-event contracts."""

from template.domain.events.user import UserRegistered
from template.integration_events.user import UserRegisteredV1


class TestUserRegisteredV1:
    """Test cases for the public user registration event."""

    def test_translates_domain_event_to_camel_case_public_contract(self):
        """
        GIVEN an internal user registration event
        WHEN it is translated into a public integration event
        THEN the JSON envelope is versioned and uses camel-case fields
        """
        # GIVEN
        event = UserRegistered(user_id="00000000-0000-0000-0000-000000000001", email="ada@example.com")

        # WHEN
        payload = UserRegisteredV1.from_domain(event).model_dump(mode="json")

        # THEN
        assert payload["eventType"] == "user.registered"
        assert payload["schemaVersion"] == 1
        assert payload["payload"] == {"userId": str(event.user_id), "email": "ada@example.com"}
