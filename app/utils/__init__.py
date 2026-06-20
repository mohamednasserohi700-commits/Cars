from app import db
from app.models import Settings


def register_context_processors(app):
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            'company_name': Settings.get('company_name', 'نظام النقل'),
            'logo': Settings.get('logo', ''),
            'theme': Settings.get('theme', 'light'),
            'now': datetime.now(),
        }
