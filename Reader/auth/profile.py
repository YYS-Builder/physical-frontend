from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from . import logger, monitor, exceptions
from .. import models, schemas

class ProfileManager:
    def __init__(self):
        self.logger = logger.logger

    async def get_profile(self, db: Session, user_id: int) -> Optional[schemas.Profile]:
        """Get a user's profile."""
        try:
            profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
            if not profile:
                return None

            self.logger.info(f"Retrieved profile for user {user_id}")
            monitor.track_request(0)  # Track profile retrieval
            return schemas.Profile.from_orm(profile)
        except Exception as e:
            self.logger.error(f"Error getting profile: {str(e)}")
            monitor.track_error("Profile", str(e))
            raise exceptions.DatabaseError("Failed to get profile")

    async def create_profile(
        self,
        db: Session,
        user_id: int,
        profile_data: Dict[str, Any]
    ) -> schemas.Profile:
        """Create a new user profile."""
        try:
            profile = models.Profile(
                user_id=user_id,
                **profile_data
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

            self.logger.info(f"Created profile for user {user_id}")
            monitor.track_request(0)  # Track profile creation
            return schemas.Profile.from_orm(profile)
        except Exception as e:
            self.logger.error(f"Error creating profile: {str(e)}")
            monitor.track_error("Profile", str(e))
            raise exceptions.DatabaseError("Failed to create profile")

    async def update_profile(
        self,
        db: Session,
        user_id: int,
        profile_data: Dict[str, Any]
    ) -> Optional[schemas.Profile]:
        """Update a user's profile."""
        try:
            profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
            if not profile:
                return None

            for key, value in profile_data.items():
                setattr(profile, key, value)

            db.commit()
            db.refresh(profile)

            self.logger.info(f"Updated profile for user {user_id}")
            monitor.track_request(0)  # Track profile update
            return schemas.Profile.from_orm(profile)
        except Exception as e:
            self.logger.error(f"Error updating profile: {str(e)}")
            monitor.track_error("Profile", str(e))
            raise exceptions.DatabaseError("Failed to update profile")

    async def delete_profile(self, db: Session, user_id: int) -> bool:
        """Delete a user's profile."""
        try:
            profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
            if not profile:
                return False

            db.delete(profile)
            db.commit()

            self.logger.info(f"Deleted profile for user {user_id}")
            monitor.track_request(0)  # Track profile deletion
            return True
        except Exception as e:
            self.logger.error(f"Error deleting profile: {str(e)}")
            monitor.track_error("Profile", str(e))
            raise exceptions.DatabaseError("Failed to delete profile")

    async def update_preferences(
        self,
        db: Session,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> Optional[schemas.Profile]:
        """Update user preferences."""
        try:
            profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
            if not profile:
                return None

            if not profile.preferences:
                profile.preferences = {}

            profile.preferences.update(preferences)
            db.commit()
            db.refresh(profile)

            self.logger.info(f"Updated preferences for user {user_id}")
            monitor.track_request(0)  # Track preferences update
            return schemas.Profile.from_orm(profile)
        except Exception as e:
            self.logger.error(f"Error updating preferences: {str(e)}")
            monitor.track_error("Profile", str(e))
            raise exceptions.DatabaseError("Failed to update preferences")

# Create global profile manager instance
profile_manager = ProfileManager() 