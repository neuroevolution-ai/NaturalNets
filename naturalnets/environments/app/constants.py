"""Contains constants for the app."""

from naturalnets.environments.app.bounding_box import BoundingBox

IMAGES_PATH: str = "naturalnets/environments/app/img/"

MAIN_PAGE_AREA_BB = BoundingBox(117, 22, 326, 420)
SETTINGS_AREA_BB = BoundingBox(3, 1, 422, 367)
