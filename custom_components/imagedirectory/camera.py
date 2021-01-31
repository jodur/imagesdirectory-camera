"""Camera that loads pictures from a local directory"""
import logging
import mimetypes
import os
import time
import datetime
from typing import Optional
from homeassistant.core import HassJob

import voluptuous as vol

from homeassistant.components.camera import (
    CAMERA_SERVICE_SCHEMA,
    PLATFORM_SCHEMA,
    Camera,
)

from homeassistant.const import ATTR_ENTITY_ID, CONF_NAME, CONF_EXCLUDE, CONF_DELAY_TIME
from . import DOMAIN,EPOCH_START,EPOCH_END,SERVICE_PARAM_SOURCE,SERVICE_PARAM_BEGINTIME,SERVCE_PARAM_ENDTIME,SERVICE_PARAM_LASTHOURS

from homeassistant.helpers import config_validation as cv

from . import Getfileslist

#camera service
SERVICE_UPDATE_IMAGE_FILELIST= "camera_update_image_filelist"
SERVICE_CLEAR_IMAGE_FILELIST='camera_clear_image_filelist'

#camera config parameters
CONF_DATA_LOCAL_FILE = "local_filelist_cameras"
CONF_DEFAULT_NAME = "Local Filelist"
CONF_PATH = SERVICE_PARAM_SOURCE
CONF_PARAM_BEGINTIME=SERVICE_PARAM_BEGINTIME
CONF_PARAM_ENDTIME=SERVCE_PARAM_ENDTIME
CONF_PARAM_LASTHOURS=SERVICE_PARAM_LASTHOURS

ALLOWED_EXT=[".jpg",".png"]

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_PATH): cv.isdir,
        vol.Optional(CONF_NAME, default=CONF_DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DELAY_TIME, default=1.0):cv.positive_float,
        vol.Optional(CONF_EXCLUDE,default=[]): cv.ensure_list,
        vol.Optional(CONF_PARAM_BEGINTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(CONF_PARAM_ENDTIME,default=EPOCH_END):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
        vol.Optional(CONF_PARAM_LASTHOURS, default=0.0):cv.positive_float,

    }
)

CAMERA_SERVICE_IMAGE_FILELIST = CAMERA_SERVICE_SCHEMA.extend(
    {
        vol.Required(CONF_PATH): cv.isdir,
        vol.Optional(CONF_EXCLUDE,default=[]): cv.ensure_list,
        vol.Optional(CONF_PARAM_BEGINTIME,default=EPOCH_START):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
		vol.Optional(CONF_PARAM_ENDTIME,default=EPOCH_END):cv.matches_regex(r'[0-3][0-9]/[0-1][0-9]/\d{4} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]'),
        vol.Optional(CONF_PARAM_LASTHOURS, default=0.0):cv.positive_float,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
   
    """Set up the Camera that works with local files."""
    if CONF_DATA_LOCAL_FILE not in hass.data:
        hass.data[CONF_DATA_LOCAL_FILE] = []

    path = config[CONF_PATH]
    delaytime= config[CONF_DELAY_TIME]
    exclude=config[CONF_EXCLUDE]
    begintime=config[CONF_PARAM_BEGINTIME]
    endtime=config[CONF_PARAM_ENDTIME]
    lasthours=config[CONF_PARAM_LASTHOURS]
    camera = LocalFile(config[CONF_NAME], path,delaytime,exclude,begintime,endtime,lasthours)
    hass.data[CONF_DATA_LOCAL_FILE].append(camera)
    

    def update_image_filelist_service(call):
        """Update the image files list"""
        path = call.data[CONF_PATH]
        entity_ids = call.data[ATTR_ENTITY_ID]
        exclude=call.data[CONF_EXCLUDE]
        begintime=call.data[CONF_PARAM_BEGINTIME]
        endtime=call.data[CONF_PARAM_ENDTIME]
        lasthours=call.data[CONF_PARAM_LASTHOURS]
        cameras = hass.data[CONF_DATA_LOCAL_FILE]

        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.update_image_filelist(path,exclude,begintime,endtime,lasthours)
        return True

    def clear_image_filelist_service(call): 
        """Clear the image files list"""  
        entity_ids = call.data[ATTR_ENTITY_ID] 
        cameras = hass.data[CONF_DATA_LOCAL_FILE]
        for camera in cameras:
            if camera.entity_id in entity_ids:
                camera.clear_image_filelist()
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
    add_entities([camera])


class LocalFile(Camera):
    """Representation of a local file camera."""

    def __init__(self, name, path, delaytime, exclude, begintime, endtime, lasthours):
        """Initialize Local File Camera component."""
        super().__init__()

        self._name = name
        self._path = path
        self._delaytime=delaytime
        self._exclude=exclude   
        self._begintime=begintime
        self._endtime=endtime   
        self._lasthours=lasthours
        self._NoImages=0
        self._fileslist= Getfileslist(self._path,self._exclude,self._begintime,self._endtime,ALLOWED_EXT,self._lasthours)
        self._NoImages= len(self._fileslist)
        _LOGGER.debug(f'No of images/files found for camera: {self._NoImages}')
        _LOGGER.debug(f"{self._fileslist}")
        self._imageindex=0 
        self._lastImageTimestamp=0.0
        self._lastimage= None
       
    
    @property #Baseclass Camera property override
    def frame_interval(self):
        """Return the interval between frames of the mjpeg stream"""
        if self._delaytime<0.5:         
            return 0.05 
        else:
            return super().frame_interval   

    
    def camera_image(self):

        #get new image when delaytime has elapsed
        if (time.time()-self._lastImageTimestamp)<self._delaytime:
            return self._lastimage

        _LOGGER.debug(f"Camera_image called {self._imageindex}")
        if self._NoImages>0:
            _LOGGER.debug(f"Load from file {self._fileslist[self._imageindex%self._NoImages]}")
            """Return image response."""
            try:
                with open(os.path.join(self._path,self._fileslist[self._imageindex%self._NoImages]), "rb") as file:
                    self._imageindex=self._imageindex+1 
                    #prevent oveflow from index
                    if self._imageindex%self._NoImages==0: self._imageindex=0
                    self._lastimage=file.read()
                    self._lastImageTimestamp=time.time()
                    return self._lastimage
                    
                    
            except FileNotFoundError:
                _LOGGER.warning(
                    "Could not read camera %s image from file: %s",
                    self._name,
                    self._file_path,
                )
            
        else:
            return None


    def update_image_filelist(self,path,exclude,begintime,endtime,lasthours):
        self._path = path
        self._exclude=exclude   
        self._begintime=begintime
        self._endtime=endtime   
        self._lasthours=lasthours
        self._NoImages=0
        self._fileslist = Getfileslist(self._path,self._exclude,self._begintime,self._endtime,ALLOWED_EXT,self._lasthours)
        self._NoImages= len(self._fileslist)
        _LOGGER.debug(f'No of images/files found for camera: {self._NoImages}')
        _LOGGER.debug(f"New filelist by service {self._fileslist}")
        self._imageindex=0 
        self.schedule_update_ha_state()

    def clear_image_filelist(self):
        self._path=''
        self._NoImages=0
        self._imageindex=0
        self._fileslist=[]
        self.schedule_update_ha_state()  


    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the camera state attributes."""
        attrs = {}
        attrs["directory"]=self._path
        attrs["imagecount"]=self._NoImages
        attrs["files"]=self._fileslist
        return attrs
