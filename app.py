import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the SQLAlchemy object (no custom model_class)
db = SQLAlchemy()

# Create Scheduler (single instance)
scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get(
        "SESSION_SECRET", "dev-secret-key-change-in-production"
    )

    # Configure the database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///triage_bot.db"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        # Import models so tables get registered against the same db registry
        import models  # noqa: F401

        # create tables
        db.create_all()

        # Register webhook blueprint
        from routes.webhook import webhook_bp

        app.register_blueprint(webhook_bp)

        # Health endpoint
        @app.route("/healthz")
        def health_check():
            return {"status": "ok", "message": "GitHub Issue Triage Bot is running"}

        # Start scheduler for stale issue detection if not already running
        try:
            from handlers.stale import check_stale_issues

            # Avoid starting duplicate scheduler when Flask debug reloader spawns two processes.
            # When using the reloader, WERKZEUG_RUN_MAIN == "true" in the child process that runs the app.
            werkzeug_run_main = os.environ.get("WERKZEUG_RUN_MAIN")
            should_start = False

            if not scheduler.running:
                # Start scheduler in production (app.debug == False) OR in the reloader child (WERKZEUG_RUN_MAIN == "true")
                if not app.debug or werkzeug_run_main == "true":
                    should_start = True

            if should_start:
                scheduler.add_job(
                    func=check_stale_issues,
                    trigger=CronTrigger(hour=9),  # Run daily at 9 AM
                    id="stale_issues_job",
                    replace_existing=True,
                )
                scheduler.start()
                logger.info("Scheduler started and stale issues job scheduled.")
            else:
                logger.debug(
                    "Scheduler not started in this process (debug reloader parent or already running)."
                )

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
