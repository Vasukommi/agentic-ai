from __future__ import annotations

from uuid import uuid4

from app.domain.actions.schemas import (
    ActionDefinition,
    ActionRunRequest,
    ActionRunResponse,
    MissingField,
)


class RunService:
    def create_run(
        self,
        action: ActionDefinition,
        request: ActionRunRequest,
    ) -> ActionRunResponse:
        normalized_inputs = self._normalize_inputs(action=action, inputs=request.inputs)
        missing_fields = self._find_missing_fields(action=action, inputs=normalized_inputs)
        run_id = str(uuid4())

        if missing_fields:
            return ActionRunResponse(
                run_id=run_id,
                action_id=action.id,
                status="needs_input",
                message="More information is needed before this action can run.",
                missing_fields=missing_fields,
                normalized_inputs=normalized_inputs,
            )

        if action.confirmation_policy.required and not request.confirmed:
            return ActionRunResponse(
                run_id=run_id,
                action_id=action.id,
                status="needs_confirmation",
                message=action.confirmation_policy.message or "Confirm this action to continue.",
                normalized_inputs=normalized_inputs,
            )

        return ActionRunResponse(
            run_id=run_id,
            action_id=action.id,
            status="completed",
            message="Action completed in dry-run mode." if request.dry_run else "Action completed.",
            normalized_inputs=normalized_inputs,
            result={
                "dry_run": request.dry_run,
                "external_call": "mocked",
            },
        )

    def _normalize_inputs(
        self,
        action: ActionDefinition,
        inputs: dict[str, object],
    ) -> dict[str, object]:
        allowed_keys = {field.key for field in action.input_fields}
        return {key: value for key, value in inputs.items() if key in allowed_keys}

    def _find_missing_fields(
        self,
        action: ActionDefinition,
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


run_service = RunService()
