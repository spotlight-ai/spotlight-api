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
        

    def test_member_already_exists_admin(client, db_session):
        """Verify that app sends conflict when owner is added, checks email exists"""
        # Setup Test
        
        # Verify owner in member table

        # Add owner to workspace

        # Verify expected response: error with conflict

        # Verify owner in database once, not more

    def test_member_promoted_to_owner(client, db_session):
        """Verify app updates database with user as non-owner to owner, keeps one row for user."""

        workspace_id = 1
        user_id = 2
        member = _get_member_in_workspace(workspace_id, user_id)
        assert len(member) == 1
        member = member[0]
        assert member.is_owner == False

        token = {
            "workspace_id": workspace_id,
            "email": member.email,
            "is_owner": True,
        }

        headers = generate_auth_headers(client, user_id=user_id)
        url = f"{workspace_route}/{workspace_id}/member"

    def test_member_already_exists_non_owner(client, db_session):
        """Verify that app sends conflict response when email already exists."""
        # Setup Test
        workspace_id = 1
        user_id = 2

        member = _get_member_in_workspace(workspace_id, user_id)
        assert len(member) == 1
        member = member[0]
        assert member is not None

        token = {
            "workspace_id": workspace_id,
            "email": member.email,
            "is_owner": False,

        }
        headers = generate_auth_headers(client, user_id=user_id)
        url = f"{workspace_route}/{workspace_id}/member"
        res = client.post(url, json=body, headers=headers)

        assert res.status_code == 409
        assert "exists" in json.loads(res.data.decode())
        assert user_id in json.loads(res.data.decode())
        assert _get_member_in_workspace(workspace_id, user_id) is len(1)


    def test_add_member_success(self, client, db_session):
        """Verify that app adds member to database via token."""
        workspace_id = 1
        expected_status = 204
        expected_message = None

        user_id = 5
        is_owner = True
        self._assert_test_add_member_success(client, workspace_id, user_id, is_owner, expected_status, expected_message)
        
        user_id = 4
        is_owner = False
        self._assert_test_add_member_success(client, workspace_id, user_id, is_owner, expected_status, expected_message)

    def _assert_test_add_member_success(client, workspace_id, user_id, is_owner, expected_status, expected_message):
        assert _get_member_in_workspace(workspace_id, user_id) is None
        owner = UserModel.query.filter_by(user_id=user_id).first()
        owner_token = {
            "workspace_id": workspace_id,
            "email": owner.email,
            "is_owner": True,
        }

        # TODO: import create_access_token?

        body = {"token": owner_token}
        headers = generate_auth_headers(client, user_id=user_id)
        res = client.post(f"{workspace_route}/{workspace_id}/member", json=body, headers=headers)
        assert res.status_code == expected_status
        assert json.loads(res.data.decode()) == expected_message
        assert _get_member_in_workspace(workspace_id, user_id) is not None


    # DELETE WorkspaceMember
    def test_delete_member_unauthorized(self, client, db_session):
        """Verify that non-owner is not authorized to delete members from workspaces."""
        workspace_id = 1
        user_id = 2
        test_delete_id = 1

        assert _get_member_in_workspace(workspace_id, user_id).is_owner is False .
        res = self._delete_member(client, workspace_id, user_id, test_delete_id)
        assert res.status_code == 401
        assert json.loads(res.data.decode()) is None
        assert _get_member_in_workspace(workspace_id, test_delete_id) is not None
        

    def test_delete_member_success(self, client, db_session):
        """Verify that app returns successful response if user exists in database or not.."""
        
        def _assert_delete_member_success(res, workspace_id, test_delete_id):
            assert res.status_code == 204
            assert json.loads(res.data.decode()) is None
            assert self._get_member_in_workspace(workspace_id, test_delete_id) is None
        
        # Test for user that exists
        workspace_id = 1
        user_id = 1
        test_delete_id = 2

        assert self._get_member_in_workspace(workspace_id, test_delete_id) is not None
        res = self._delete_member(client, workspace_id, user_id, test_delete_id)
        _assert_delete_member_success(res, workspace_id, test_delete_id)

        # Test for user that does not exist
        workspace_id = 1
        user_id = 1
        test_delete_id = 900

        member_query = self._get_member_in_workspace(workspace_id, test_delete_id)
        
        res = self._delete_member(client, workspace_id, user_id, test_delete_id)
        _assert_delete_member_success(res, workspace_id, test_delete_id)
    
    def _delete_member(client, workspace_id, user_id, test_delete_id):
        
        headers = generate_auth_headers(client, user_id=user_id)

        # Delete Member
        res = client.delete(
            f"{workspace_route}/{workspace_id}/member",
            json={
                "user_id": {test_delete_id}
            },
            headers=headers
        )
        return res

    def _get_member_in_workspace(workspace_id, user_id):
        return WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id,
        ).all()

    def _assert_member_exists(result):
        assert result is not None
        assert type(result) is list
        assert len(result) == 1

    def _assert_member_does_not_exist(result):
        if result:
            assert len(result) == 0
        else:
            assert True
