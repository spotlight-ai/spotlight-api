from tests.conftest import workspace_route
from tests.conftest import generate_auth_headers

class WorkspaceCollectionTest:
    def test_add_workspace_success():
        """Verify that workspace resource is created."""
        assert res.status_code == 201
        # Setup test

        # Verify workspace with name does not exist

        # Add workspace

        # Verify expected response: successful resource created

        # Verify workspace with name in database

    def test_add_workspace_conflict():
        """Verify that workspace with same name returns conflict."""
        # Setup Test

        # Verify workspace with name exists in database

        # Add workspace

        # Verify expected response: error with conflict

        # Verify workspace in database appears only once, was the old record.???


class WorkspaceInvitationTest:
    def test_invite_send_success():
        """Verify email sent? """
        assert res.status_code == 204 

        # Setup Test

        # Verify invite user is not in database

        # Send invite

        # Verify expected response: successful no content


    def test_send_invite_unauthorized(client, db_session):
        """Verify non owner of workspace cannot send invitation."""
        assert res.status_code == 401

        # Setup Test

        # Verify user is not owner in database

        # Send invite

        # Verify expected response: 401 unauthorized
        

    def test_invite_validate_success():
        """Verify that response sent is 200 OK for client to create a Spotlight user account."""
        # Setup Test
        # Verify user not in user table
        # Send validate request
        # Verify expected response - 200

    def test_invite_validate_fail():
        """Verify that response sent is unauthorized, client should not make user account to add to workspace."""
        # Setup Test
        # Verify user in user table
        # Send validate request
        # Verify expected response - 409 conflict user account already exists


class WorkspaceMemberCollectionTest:

    def test_add_member_missing_token(client, db_session):
        """Verify invalid request when token is not in request."""
        # Setup Test
        # Verify user not in database
        # Verify expected response: bad request
        # Verify user not in database

    def test_user_in_token_does_not_match(client, db_session):
        """Verify that authenticated user is unauthorized with wrong invite token."""
        # Setup Test
        # Verify user not in database as member
        # Verify expected resopnse: unauthorized request
        # Verify user not in database as member

    def test_token_owner_workspace_owner_do_not_match(client, db_session):
        """Verify that authenticated user is unauthorized with wrong token."""
        # Setup Test with different user_id and token_user_id

        # Verify user_id not in database as owner

        # Verify expected response: unauthorized request

        # Verify owner not in database


    def test_owner_id_in_token_behavior(client, db_session):
        ???

    def test_workspace_id_in_token_behavior(client, db_session):
        ???

    def test_member_already_exists_admin(client, db_session):
        """Verify that app sends conflict when owner is added, checks email exists"""
        # Setup Test
        
        # Verify owner with email in database

        # Add owner to workspace

        # Verify expected response: error with conflict

        # Verify owner in database once, not more

    def test_member_promoted_to_owner(client, db_session):
        """Verify app updates database with user as non-owner to owner, keeps one row for user."""

    def test_member_already_exists_non_owner(client, db_session):
        """Verify that app sends conflict response when email already exists."""
        # Setup Test

        # Verify user with email in database

        # Add user to workspace

        # Verify expected response: error with conflict
        assert res.status_code == 409

        # Verify user in database once, not more

    def test_add_owner_success(client, db_session):
        """Verify that app adds workspace owner via token."""
        # Setup Test with owner token

        # Verify owner not in database

        # Add owner to workspace

        # Verify expected response: successful resource added

        # Verify owner in database


    def test_add_member_success(client, db_session):
        """Verify that app adds member to database via token."""
        # Setup Test with invite token

        # Verify member not in database

        # Add user to workspace

        # Verify expected response: successful resource added
        assert res.status_code == 201

        # Verify member in database

    # DELETE WorkspaceMember
    def test_delete_member_unauthorized(client, db_session):
        """Verify that non-owner is not authorized to delete members from workspaces."""
        # Setup Test

        # Verify user is not owner of workspace, member to delete is in database

        # Attempt deletion of other member

        # Verify expected response: unauthorized

        # Verify member was not deleted from database
        

    def test_delete_member_does_not_exist(client, db_session):
        """Verify that app returns successful even when member did not exist previously."""
        # Setup Test

        # Verify member NOT in database

        # Delete member

        # Verify expected response: successful as if member was in table

        # Verify member not in database

        assert res.status_code == 204
    
    def test_delete_member_success(client, db_session):
        """Verify successful deletion of member that was in workspace."""

        # Setup Test
        owner_id = 1
        test_delete_id = 2
        workspace_id = 1

        headers = generate_auth_headers(client, user_id=owner_id)

        # Verify member in database

        # Delete Member
        res = client.delete(
            f"{workspace_route}/{workspace_id}/member",
            json={
                "user_id": {test_delete_id}
            },
            headers=headers
        )

        # Verify expected response: successful delete with no content response
        assert res.status_code == 204
        assert "deleted" in json.loads(res.data.decode())
        assert test_delete_id in json.loads(res.data.decode())

        # Verify member not in database
        workspace_members = WorkspaceMemberModel.query.filter_by(workspace_id=workspace_id).all()
        assert test_delete_id not in map(lambda x: x.user_id, workspace_members)
