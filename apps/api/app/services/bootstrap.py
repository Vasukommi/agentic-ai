from app.models.app import SaasApp
from app.models.organization import Organization

DEFAULT_ORGANIZATION_SLUG = "demo-org"
DEFAULT_APP_SLUG = "demo-app"


def get_or_create_default_app(db) -> SaasApp:
    organization = (
        db.query(Organization)
        .filter(Organization.slug == DEFAULT_ORGANIZATION_SLUG)
        .first()
    )
    if organization is None:
        organization = Organization(name="Demo Organization", slug=DEFAULT_ORGANIZATION_SLUG)
        db.add(organization)
        db.flush()

    app = (
        db.query(SaasApp)
        .filter(SaasApp.organization_id == organization.id, SaasApp.slug == DEFAULT_APP_SLUG)
        .first()
    )
    if app is None:
        app = SaasApp(
            organization_id=organization.id,
            name="Demo App",
            slug=DEFAULT_APP_SLUG,
            environment="development",
        )
        db.add(app)
        db.flush()

    return app
