from __future__ import annotations

from uuid import uuid4

from app.domain.actions.schemas import (
    ActionRunRecord,
    ActionRunRequest,
    ActionRunResponse,
    MissingField,
)
from app.models.action import Action
from app.models.app_session import AppSession
from app.models.audit_event import AuditEvent
from app.models.run import Run
from app.services.action_registry import action_service


class RunService:
    def list_runs(self, db, limit: int = 50) -> list[ActionRunRecord]:
        runs = db.query(Run).order_by(Run.created_at.desc()).limit(limit).all()
        return [
            ActionRunRecord(
                run_id=run.id,
                action_id=run.action.key if run.action else "",
                status=run.status,
                message=run.message,
                missing_fields=run.missing_fields,
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
        missing_fields = self._find_missing_fields(
            action=action_definition,
            inputs=normalized_inputs,
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
