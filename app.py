import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///triage_bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

def create_app():
    with app.app_context():
        # Import models to ensure tables are created
        import models
        db.create_all()
        
        # Register webhook blueprint
        from routes.webhook import webhook_bp
        app.register_blueprint(webhook_bp)
        
        # Start scheduler for stale issue detection
        from handlers.stale import check_stale_issues
        if not scheduler.running:
            scheduler.add_job(
                func=check_stale_issues,
                trigger=CronTrigger(hour=9),  # Run daily at 9 AM
                id='stale_issues_job',
                replace_existing=True
            )
            scheduler.start()
            
    return app

@app.route('/healthz')
def health_check():
    return {"status": "ok", "message": "GitHub Issue Triage Bot is running"}

if __name__ == '__main__':
    create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)