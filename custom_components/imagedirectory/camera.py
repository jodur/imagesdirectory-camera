"""Camera that loads pictures from a local directory"""
import asyncio
from aiohttp import web
import logging
import mimetypes
import os
import time
import datetime
from typing import Optional
from homeassistant.core import HassJob

import voluptuous as vol

from homeassistant.components.camera import (
    PLATFORM_SCHEMA,
    Camera,
)

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_NAME,
    CONF_EXCLUDE,
    CONF_DELAY_TIME,
    SERVICE_TOGGLE,
    CONTENT_TYPE_MULTIPART,
    STATE_PAUSED,
)
from . import (
    DOMAIN,
    EPOCH_START,
    EPOCH_END,
    SERVICE_PARAM_SOURCE,
    SERVICE_PARAM_BEGINTIME,
    SERVCE_PARAM_ENDTIME,
    SERVICE_PARAM_LASTHOURS,
)

from homeassistant.helpers import config_validation as cv

from . import Getfileslist


# camera service
SERVICE_UPDATE_IMAGE_FILELIST = "camera_update_image_filelist"
SERVICE_CLEAR_IMAGE_FILELIST = "camera_clear_image_filelist"
SERVICE_TOGGLE_PAUSE = "Camera_toggle_pause"
SERVICE_NEXT = "Camera_next_image"
SERVICE_PREV = "Camera_prev_image"

# camera config parameters
CONF_DATA_LOCAL_FILE = "local_filelist_cameras"
CONF_DEFAULT_NAME = "Local Filelist"
CONF_PATH = SERVICE_PARAM_SOURCE
CONF_PARAM_BEGINTIME = SERVICE_PARAM_BEGINTIME
CONF_PARAM_ENDTIME = SERVCE_PARAM_ENDTIME
CONF_PARAM_LASTHOURS = SERVICE_PARAM_LASTHOURS

# camera states
STATE_STREAMING = "streaming"


ALLOWED_EXT = [".jpg", ".png"]

_LOGGER = logging.getLogger(__name__)

CAMERA_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PATH): cv.isdir,
        vol.Optional(CONF_NAME, default=CONF_DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DELAY_TIME, default=1.0): cv.positive_float,
        vol.Optional(CONF_EXCLUDE, default=[]): cv.ensure_list,
        vol.Optional(CONF_PARAM_BEGINTIME, default=EPOCH_START): cv.matches_regex(
            r"[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        ),
        vol.Optional(CONF_PARAM_ENDTIME, default=EPOCH_END): cv.matches_regex(
            r"[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        ),
        vol.Optional(CONF_PARAM_LASTHOURS, default=0.0): cv.positive_float,
    }
)

CAMERA_SERVICE_IMAGE_FILELIST = CAMERA_SERVICE_SCHEMA.extend(
    {
        vol.Required(CONF_PATH): cv.isdir,
        vol.Optional(CONF_EXCLUDE, default=[]): cv.ensure_list,
        vol.Optional(CONF_PARAM_BEGINTIME, default=EPOCH_START): cv.matches_regex(
            r"[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        ),
        vol.Optional(CONF_PARAM_ENDTIME, default=EPOCH_END): cv.matches_regex(
            r"[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        ),
        vol.Optional(CONF_PARAM_LASTHOURS, default=0.0): cv.positive_float,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):

    """Set up the Camera that works with local files."""
    if CONF_DATA_LOCAL_FILE not in hass.data:
        hass.data[CONF_DATA_LOCAL_FILE] = []

    path = config[CONF_PATH]
    delaytime = config[CONF_DELAY_TIME]
    exclude = config[CONF_EXCLUDE]
    begintime = config[CONF_PARAM_BEGINTIME]
    endtime = config[CONF_PARAM_ENDTIME]
    lasthours = config[CONF_PARAM_LASTHOURS]
    camera = LocalFile(
        config[CONF_NAME], path, delaytime, exclude, begintime, endtime, lasthours
    )
    hass.data[CONF_DATA_LOCAL_FILE].append(camera)

    def update_image_filelist_service(call):
        """Update the image files list"""
        path = call.data[CONF_PATH]
        entity_ids = call.data[ATTR_ENTITY_ID]
        exclude = call.data[CONF_EXCLUDE]
        begintime = call.data[CONF_PARAM_BEGINTIME]
        endtime = call.data[CONF_PARAM_ENDTIME]
        lasthours = call.data[CONF_PARAM_LASTHOURS]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]

        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.update_image_filelist(
                    path, exclude, begintime, endtime, lasthours
                )
        return True

    def clear_image_filelist_service(call):
        """Clear the image files list"""
        entity_ids = call.data[ATTR_ENTITY_ID]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]
        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.clear_image_filelist()
        return True

    def toggle_pause_filelist_service(call):
        # next image
        entity_ids = call.data[ATTR_ENTITY_ID]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]
        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.toggle_pause()
        return True

    def next_image_filelist_service(call):
        # next image
        entity_ids = call.data[ATTR_ENTITY_ID]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]
        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.load_next_image()
        return True

    def prev_image_filelist_service(call):
        # next image
        entity_ids = call.data[ATTR_ENTITY_ID]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]
        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.load_prev_image()
        return True

    hass.services.register(
        DOMAIN,
        SERVICE_UPDATE_IMAGE_FILELIST,
        update_image_filelist_service,
        schema=CAMERA_SERVICE_IMAGE_FILELIST,
    )
    hass.services.register(
        DOMAIN,
        SERVICE_CLEAR_IMAGE_FILELIST,
        clear_image_filelist_service,
        schema={},
    )
    hass.services.register(
        DOMAIN,
        SERVICE_TOGGLE_PAUSE,
        toggle_pause_filelist_service,
        schema={},
    )
    hass.services.register(
        DOMAIN,
        SERVICE_NEXT,
        next_image_filelist_service,
        schema={},
    )
    hass.services.register(
        DOMAIN,
        SERVICE_PREV,
        prev_image_filelist_service,
        schema={},
    )
    add_entities([camera])


async def async_get_still_stream(request, image_cb, content_type, interval):
    """Generate an HTTP MJPEG stream from camera images.
    The original implementation in the HA core camera
    component, had some issues in displaying the images
    The view was always 1 frame behind
    so thats why it was in the original code to send twice at start.
    Normally not a problem, but in this component it is essential that the
    image that is served is also displayed
    """
    response = web.StreamResponse()
    response.content_type = CONTENT_TYPE_MULTIPART.format("--frameboundary")
    await response.prepare(request)

    async def write_to_mjpeg_stream(img_bytes):
        """Write image to stream."""
        await response.write(
            bytes(
                "--frameboundary\r\n"
                "Content-Type: {}\r\n"
                "Content-Length: {}\r\n\r\n".format(content_type, len(img_bytes)),
                "utf-8",
            )
            + img_bytes
            + b"\r\n"
        )

    LastImage = None
    SameImagecount = 0
    while True:
        img_bytes = await image_cb()
        if not img_bytes:
            break
        # Send same image max 2 times, to fix browserproblem
        if img_bytes == LastImage:
            SameImagecount += 1
        else:
            SameImagecount = 0

        if SameImagecount < 2:
            await write_to_mjpeg_stream(img_bytes)
            LastImage = img_bytes

        await asyncio.sleep(interval)
    return response


class LocalFile(Camera):
    """Representation of a local file camera."""

    def __init__(self, name, path, delaytime, exclude, begintime, endtime, lasthours):
        """Initialize Local File Camera component."""
        super().__init__()

        self._name = name
        self._path = path
        self._delaytime = delaytime
        self._exclude = exclude
        self._begintime = begintime
        self._endtime = endtime
        self._lasthours = lasthours
        self._NoImages = 0
        self._fileslist = Getfileslist(
            self._path,
            self._exclude,
            self._begintime,
            self._endtime,
            ALLOWED_EXT,
            self._lasthours,
        )
        self._NoImages = len(self._fileslist)
        _LOGGER.debug(f"No of images/files found for camera: {self._NoImages}")
        _LOGGER.debug(f"{self._fileslist}")
        self._imageindex = -1
        self._lastImageTimestamp = 0.0
        self._lastimage = None
        self._pause = False

    @property  # Baseclass Camera property override
    def frame_interval(self):
        """Return the interval between frames of the mjpeg stream"""
        if self._delaytime < 0.5:
            return 0.05
        else:
            return super().frame_interval

    def load_next_image(self):
        if self._NoImages > 0:
            self._imageindex = self._imageindex + 1
            """Return image response."""
            # When end of list reached set to begin
            if self._imageindex > (self._NoImages - 1):
                self._imageindex = 0
            _LOGGER.debug(
                f"Load [{self._imageindex}] from file {self._fileslist[self._imageindex]}"
            )
            try:
                with open(
                    os.path.join(self._path, self._fileslist[self._imageindex]), "rb"
                ) as file:
                    self._lastimage = file.read()
                    self._lastImageTimestamp = time.time()
                    return self._lastimage
            except FileNotFoundError:
                _LOGGER.warning(
                    "Could not read camera %s image from file: %s",
                    self._name,
                    self._file_path,
                )
        else:
            return None

    def load_prev_image(self):
        if self._NoImages > 0:
            """Return image response."""
            self._imageindex = self._imageindex - 1
            # When begining of list reached
            if self._imageindex < 0:
                self._imageindex = 0
            _LOGGER.debug(
                f"Load [{self._imageindex}] from file {self._fileslist[self._imageindex]}"
            )
            try:
                with open(
                    os.path.join(self._path, self._fileslist[self._imageindex]), "rb"
                ) as file:
                    self._lastimage = file.read()
                    self._lastImageTimestamp = time.time()
                    return self._lastimage
            except FileNotFoundError:
                _LOGGER.warning(
                    "Could not read camera %s image from file: %s",
                    self._name,
                    self._file_path,
                )
        else:
            return None

    def camera_image(self):

        # reset pause after 1 min
        if self._pause and (time.time() - self._lastImageTimestamp) > 60:
            self.toggle_pause()

        # get new image when delaytime has elapsed
        if ((time.time() - self._lastImageTimestamp) < self._delaytime) or self._pause:
            return self._lastimage
        else:
            return self.load_next_image()

    async def async_camera_image(self):
        """Return bytes of camera image."""
        return await self.hass.async_add_executor_job(self.camera_image)

    async def handle_async_still_stream(self, request, interval):
        """Generate an HTTP MJPEG stream from camera images."""
        return await async_get_still_stream(
            request, self.async_camera_image, self.content_type, interval
        )

    async def handle_async_mjpeg_stream(self, request):
        """Serve an HTTP MJPEG stream from the camera."""
        return await self.handle_async_still_stream(request, self.frame_interval)

    def toggle_pause(self):
        self._pause = not self._pause
        self.schedule_update_ha_state()

    def update_image_filelist(self, path, exclude, begintime, endtime, lasthours):
        self._path = path
        self._exclude = exclude
        self._begintime = begintime
        self._endtime = endtime
        self._lasthours = lasthours
        self._NoImages = 0
        self._fileslist = Getfileslist(
            self._path,
            self._exclude,
            self._begintime,
            self._endtime,
            ALLOWED_EXT,
            self._lasthours,
        )
        self._NoImages = len(self._fileslist)
        _LOGGER.debug(f"No of images/files found for camera: {self._NoImages}")
        _LOGGER.debug(f"New filelist by service {self._fileslist}")
        self._imageindex = -1
        self.schedule_update_ha_state()

    def clear_image_filelist(self):
        self._path = ""
        self._NoImages = 0
        self._imageindex = -1
        self._fileslist = []
        self.schedule_update_ha_state()

    @property
    def state(self):
        """Return the camera state."""
        if self._pause:
            return STATE_PAUSED
        return STATE_STREAMING

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def extra_state_attributes(self):
        """Return the camera state attributes."""
        attrs = {}
        attrs["directory"] = self._path
        attrs["imagecount"] = self._NoImages
        attrs["files"] = self._fileslist
        return attrs
