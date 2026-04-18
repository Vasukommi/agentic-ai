from __future__ import annotations

import re
from datetime import date, datetime
from uuid import uuid4

from app.domain.actions.schemas import (
    ActionRunRecord,
    ActionRunRequest,
    ActionRunResponse,
    InvalidField,
    MissingField,
)
from app.models.action import Action
from app.models.app_session import AppSession
from app.models.audit_event import AuditEvent
from app.models.run import Run
from app.services.action_registry import action_service

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RunService:
    def list_runs_for_session(
        self,
        db,
        app_session: AppSession,
        limit: int = 50,
    ) -> list[ActionRunRecord]:
        query = db.query(Run).filter(Run.app_id == app_session.app_id)
        if app_session.tenant_ref:
            query = query.filter(Run.tenant_ref == app_session.tenant_ref)

        if "runs:read_all_tenant" not in app_session.permissions:
            query = query.filter(Run.end_user_ref == app_session.end_user_ref)

        runs = query.order_by(Run.created_at.desc()).limit(limit).all()
        return [
            ActionRunRecord(
                run_id=run.id,
                action_id=run.action.key if run.action else "",
                status=run.status,
                message=run.message,
                missing_fields=run.missing_fields,
                invalid_fields=run.result.get("invalid_fields", []),
                normalized_inputs=run.normalized_inputs,
                result=run.result,
                end_user_ref=run.end_user_ref,
                tenant_ref=run.tenant_ref,
                created_at=run.created_at,
            )
            for run in runs
        ]

    def create_run(
        self,
        db,
        action: Action,
        request: ActionRunRequest,
        app_session: AppSession,
    ) -> ActionRunResponse:
        action_definition = action_service.to_definition(action)
        normalized_inputs = self._normalize_inputs(action=action_definition, inputs=request.inputs)
        invalid_fields = self._find_invalid_fields(
            action=action_definition,
            raw_inputs=request.inputs,
            normalized_inputs=normalized_inputs,
        )
        missing_fields = self._find_missing_fields(
            action=action_definition,
            inputs=normalized_inputs,
        )

        if invalid_fields:
            return self._persist_response(
                db=db,
                action=action,
                request=request,
                app_session=app_session,
                response=ActionRunResponse(
                    run_id=str(uuid4()),
                    action_id=action.key,
                    status="failed",
                    message="Provided inputs did not match the action contract.",
                    missing_fields=missing_fields,
                    invalid_fields=invalid_fields,
                    normalized_inputs=normalized_inputs,
                    result={
                        "invalid_fields": [field.model_dump() for field in invalid_fields],
                    },
                ),
            )

        if missing_fields:
            return self._persist_response(
                db=db,
                action=action,
                request=request,
                app_session=app_session,
                response=ActionRunResponse(
                    run_id=str(uuid4()),
                    action_id=action.key,
                    status="needs_input",
                    message="More information is needed before this action can run.",
                    missing_fields=missing_fields,
                    invalid_fields=invalid_fields,
                    normalized_inputs=normalized_inputs,
                ),
            )

        if action_definition.confirmation_policy.required and not request.confirmed:
            return self._persist_response(
                db=db,
                action=action,
                request=request,
                app_session=app_session,
                response=ActionRunResponse(
                    run_id=str(uuid4()),
                    action_id=action.key,
                    status="needs_confirmation",
                    message=action_definition.confirmation_policy.message
                    or "Confirm this action to continue.",
                    invalid_fields=invalid_fields,
                    normalized_inputs=normalized_inputs,
                ),
            )

        return self._persist_response(
            db=db,
            action=action,
            request=request,
            app_session=app_session,
            response=ActionRunResponse(
                run_id=str(uuid4()),
                action_id=action.key,
                status="completed",
                message=(
                    "Action completed in dry-run mode."
                    if request.dry_run
                    else "Action completed."
                ),
                invalid_fields=invalid_fields,
                normalized_inputs=normalized_inputs,
                result={
                    "dry_run": request.dry_run,
                    "external_call": "mocked",
                },
            ),
        )

    def _normalize_inputs(
        self,
        action,
        inputs: dict[str, object],
    ) -> dict[str, object]:
        allowed_keys = {field.key for field in action.input_fields}
        return {key: value for key, value in inputs.items() if key in allowed_keys}

    def _find_missing_fields(
        self,
        action,
        inputs: dict[str, object],
    ) -> list[MissingField]:
        missing_fields = []
        for field in action.input_fields:
            if not field.required:
                continue

            value = inputs.get(field.key)
            if value is None or value == "":
                missing_fields.append(
                    MissingField(
                        key=field.key,
                        label=field.label,
                        kind=field.kind,
                        description=field.description,
                    )
                )

        return missing_fields

    def _find_invalid_fields(
        self,
        action,
        raw_inputs: dict[str, object],
        normalized_inputs: dict[str, object],
    ) -> list[InvalidField]:
        invalid_fields = []
        field_map = {field.key: field for field in action.input_fields}

        for key in raw_inputs:
            if key not in field_map:
                invalid_fields.append(
                    InvalidField(
                        key=key,
                        label=key,
                        reason="Unknown field.",
                    )
                )

        for key, value in normalized_inputs.items():
            if value in (None, ""):
                continue

            field = field_map[key]
            error_message = self._validate_field_value(field, value)
            if error_message is not None:
                invalid_fields.append(
                    InvalidField(
                        key=field.key,
                        label=field.label,
                        reason=error_message,
                    )
                )

        return invalid_fields

    def _validate_field_value(self, field, value: object) -> str | None:
        if field.kind == "string":
            return None if isinstance(value, str) else "Expected a string."

        if field.kind == "number":
            return None if isinstance(value, (int, float)) and not isinstance(value, bool) else (
                "Expected a number."
            )

        if field.kind == "integer":
            return None if isinstance(value, int) and not isinstance(value, bool) else (
                "Expected an integer."
            )

        if field.kind == "boolean":
            return None if isinstance(value, bool) else "Expected a boolean."

        if field.kind == "email":
            if not isinstance(value, str):
                return "Expected an email address."
            return None if EMAIL_PATTERN.match(value) else "Expected a valid email address."

        if field.kind == "enum":
            if not isinstance(value, str):
                return "Expected one of the allowed values."
            return None if value in field.enum_values else "Value is not in the allowed set."

        if field.kind == "object":
            return None if isinstance(value, dict) else "Expected an object."

        if field.kind == "date":
            if not isinstance(value, str):
                return "Expected an ISO date string."
            try:
                date.fromisoformat(value)
            except ValueError:
                return "Expected an ISO date string."
            return None

        if field.kind == "datetime":
            if not isinstance(value, str):
                return "Expected an ISO datetime string."
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return "Expected an ISO datetime string."
            return None

        return None

    def _persist_response(
        self,
        db,
        action: Action,
        request: ActionRunRequest,
        app_session: AppSession,
        response: ActionRunResponse,
    ) -> ActionRunResponse:
        run = Run(
            id=response.run_id,
            app_id=action.app_id,
            action_id=action.id,
            session_id=app_session.id,
            status=response.status,
            message=response.message,
            inputs=request.inputs,
            normalized_inputs=response.normalized_inputs,
            missing_fields=[field.model_dump() for field in response.missing_fields],
            result=response.result,
            confirmed=request.confirmed,
            dry_run=request.dry_run,
            end_user_ref=app_session.end_user_ref,
            tenant_ref=app_session.tenant_ref,
        )
        db.add(run)
        db.flush()

        db.add(
            AuditEvent(
                organization_id=action.app.organization_id,
                app_id=action.app_id,
                run_id=run.id,
                event_type=f"run.{response.status}",
                summary=f"Action {action.key} finished with status {response.status}.",
                event_metadata={
                    "action_key": action.key,
                    "dry_run": request.dry_run,
                    "confirmed": request.confirmed,
                    "session_id": app_session.id,
                    "end_user_ref": app_session.end_user_ref,
                    "tenant_ref": app_session.tenant_ref,
                    "roles": app_session.roles,
                    "permissions": app_session.permissions,
                },
            )
        )
        db.commit()
        return response


run_service = RunService()
