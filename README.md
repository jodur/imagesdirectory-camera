[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)
# Imagedirectory
Homeassistant custom component for serveral operations on snapshots images and display the images in a **homeassistant camera** entity.

Supported operations:
- compose an animated GIF or MP4 of selected snapshot (PNG, JPEG)
- delete or move files (JPG,PNG,GIF and MP4)
- looping timelaps camera for selected snapshots/images

****
This component was developed by my need of creating a looping animation from snapshot images that where created by the deepstack custom component.

This integration provides 3 methods for this:
- create a animated GIF
- create a mp4 video 
- display the snapshots with a camera entity within homeassistant
	The camera is using the selected snapshots directly from files  **without** a intermediate format

The platform is designed for general use of converting snapshots to animated GIF or MP4, so it is useful for everyone who has to handle or deal with snapshots created by cameras of image processing software. The component can also be used to create a slideshow of pictures or create a timelaps video/camera from pictures in a directory

# Platform setup

To use this component, copy the directory `imagedirectory`and it contents to the `custom_components` directory of your homeassistant or use hacs and add this repository as custom repository to hacs.

Add the following line in your `configuration.yaml:`
```yaml
imagedirectory:
```
Restart home-assistant after this.

If the custom component is installed correctly you should have the following services available: 

`imagedirectory.create`
This service is used to create of animated GIF or MP4 from selected files

`imagedirectory.move`
This service is used to move selected files (PNG,JPG,GIF or MP4) to another direcory

`imagedirectory.delete`
This service is used to delete selected files (PNG,JPG,GIF or MP4)

These services could be easily found under the development tools, tab services.

###### Usage:

### **imagedirectory.create_gif_mp4**

This service has to be called with the following calll-parameters:


| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath  |  	path of the directory where the snaphots are in | mandatory, directory must exist  |
|  destinationpath |  path of the directory where the GIF should be created |  mandatory, directory must exist |
|  filename |	Name for gif/mp3 file (without extension)   | optional, default=latest  |
|  format |  `gif` or `mp4` | optional, default='gif'   |
| exclude  |  list of files to exclude in conversion |optional   |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |

## File selection

With the parameter `exclude` you could **exclude** certain files that should not be added in the created output file (gif or mp4)

Most solutions create a timestamped snapshot file and also a snapshot file with a fixed filename (for exampe: deepstack_object_xxxx_latest.jpg).  In most cases you want to exclude such a file in the output file.

##### Time range selection
The begin and end timestamps are useful for selecting the snapshot files you want within a certain timeframe 
(**N.B. this is the creation time of the file , not a timestamp format in the filename**). 

The combination of both timestamps will have a different filter behaviour

`begintimestamp` and `endtimestamp `defined:
Files with **creation time** within the give range  [`begintimestamp`,`endtimestamp`] wil be selected and proccesed for the output file.

**No** `begintimestamp` and `endtimestamp `defined:
Als files in the directory will be selected

Only `begintimestamp` is defined:
Files with **creation time** greater or equal then `begintimestamp`wil be selected and proccesed for the output file.

Only `endtimestamp` is defined:
Files with **creation time** less or equal then `endtimestamp`wil be selected and proccesed for the output file.

Example for usage:


| Parameter  |Value   |
| ------------ | ------------ |
| sourcepath:  |  /config/snapshots/oprit |
| destinationpath:  | /config/www  |
| filename:   |latest_oprit   |
| exclude: | deepstack_object_camera_oprit_latest.jpg  |
| begintimestamp | '25/12/2020 23:24:24'  |
| endtimestamp: | '25/12/2020 23:24:40  |

### **imagedirectory.delete**
| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath  |  	directory where the snaphots are in | mandatory, directory must exist  |
| exclude  |  list of files to exclude in conversion |optional   |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |

The file selection function defined by exclude and the timestamps are identical as in the use with `imagedirectory.create_gif_mp4`

### **imagedirectory.move**
| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath  |  	path of the directory where the snaphots are in | mandatory, directory must exist  |
|  destinationpath |  path of the directory where the files should moved|  mandatory, directory must exist |
| exclude  |  list of files to exclude in conversion |optional   |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |

The file selection function defined by exclude and the timestamps are identical as in the use with `imagedirectory.create_gif_mp4`

### Events

When a service is called, an event will be triggerd after **succesful** operation of the service. This event could be used for example for notifications to the mobile app when a Gif or MP4 is created.

The event to listen for is: `imagedirectory`

This could also be easily explored with the developers tool event viewer, were you can listen to this event. 

The field `Type` within the event data can be used to distinguish between the originated service of the event.

The event data contains information about the operation of the service:
### Example event data:
For example the event, in case of the service call: ` imagedirectort.create_gif_mp4`
```json
{
    "event_type": "imagedirectory",
    "data": {
        "Type": "create_gif_mp4",
        "file": "mylatest.gif",
        "Path": "/config/www",
        "BeginTimeStamp": "26/12/2020 14:17:00",
        "EndTimeStamp": "26/12/2020 14:17:59",
        "NoComposedImages": 9,
        "sourcepath": "/config/snapshots/achtertuin",
        "sourcefiles": [
            "deepstack_object_achtertuin_2020-12-26_14-17-02.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-03.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-04.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-06.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-07.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-08.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-14.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-15.jpg",
            "deepstack_object_achtertuin_2020-12-26_14-17-16.jpg"
        ]
    },
    "origin": "LOCAL",
    "time_fired": "2020-12-26T21:37:36.411617+00:00",
    "context": {
        "id": "a3340e0c0b66813d7a18ac93effaa0da",
        "parent_id": null,
        "user_id": null
    }
}
```
# Camera entity

Altough the generated gif or mp4 could be easily displayed using the existing available camera entities in homeassistant, the availbilty of a camera component that is capable of directly serving the images to a camera component is much easier, more flexible and more user friendly.

## Configuration
To enable this camera in your installation, you must first have an existing directory with images files
Next, add the following to your `configuration.yaml` file in the camera section:


```yaml
camera:
  - platform: imagedirectory
     name: achtertuin_motion
     sourcepath: /config/snapshots/achtertuin
     excludelist: deepstack_object_achtertuin_latest.jpg 
     lasthours: 2.0
```
The example above selects only the files, from the last 2 hours, since the time of the latest file in the directory `/config/snapshots/achtertuin` to display in the camera with a default delay of 1 sec between the images.


## Configuration variables

| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
| sourcepath |  	directory where the snaphots are in | mandatory, directory must exist  |
| exclude  |  list of files to exclude in the camera| optional |
| delay_time |  Time in sec. between 2 frames in camera |optional, Default 1.0 s)  |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |
| lasthours  |  Select only files from last x hours since lastfile in selected timerange| optional, Default=0.0 =>select all files in the timerange |

The file selection function defined by exclude and the timestamps are identical as in the use with `imagedirectory.create_gif_mp4` service.

The only addition is the `lasthours` parameter that allows you to select only the latest `x.x` hours from the latest images within the given timerange. This parameters allows you to only include the snapshots that are made (for example) the last 2 hours to display in the camera.

The No. of files and the selected files that the camera is using are available as Attribute and could be examined under the developer tools under the STATES tab.

## Camera services

The imagelist that the camera is using can be changed with  2 available service :

`imagedirectory.camera_update_image_filelist` and `imagedirectory.camera_clear_image_filelist`

#### SERVICE : imagedirectory.camera_update_image_filelist

This service allows you to change the images the camera is using.

| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
|entity_id |  entity_id of camera | mandatory  |
| sourcepath |  	directory where the snaphots are in | mandatory, directory must exist  |
| exclude  |  list of files to exclude in the camera| optional |
| delay_time |  Time in sec. between 2 frames in camera |optional, Default 1.0 s)  |
| begintimestamp  |  begin timestamp | optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |
| endtimestamp  | end timestamp  |  optional, format 'mm/dd/yyyy hh:mm:ss'   |
| lasthours  |  Select only files from last x hours since lastfile in selected timerange| optional, Default=0.0 =>select all files in the timerange |

For explanation of the parameters see cofiguration parameters camera.

#### SERVICE : imagedirectory.camera_clear_image_filelist

This service clears the imagelist that the camera is using. The camera will blank after this service. This service is manly used when you  want to move or delete images with the other service described earlier.

| Parameter  | Description  | additional  |
| ------------ | ------------ | ------------ |
|entity_id |  entity_id of camera | mandatory  |

# Examples (Use cases):

### Example 1: Deepstack object detection 
This example uses deepstack and the deepstack_object_detection by [@robmarkcole](https://github.com/robmarkcole/HASS-Deepstack-object "@robmarkcole") to detect objects in my camera feed.

The workflow with the underlying steps is as following:

**Step 1**
I have a input_boolean that signals that motion is detected. This could be a sensor or in my case a motion detection signal from the camera stream.  This triggers the automation
**Step 2**
The timestamp is saved in a variable, to mark the beginning of detection that could be used later on for the imagedirectory services.

**Step 3**
While motion is detected a camera image is send to  deepstack (using the service `image_processing.scan` from the [deepstack_object_integration](https://github.com/robmarkcole/HASS-Deepstack-object "deepstack_object_integration"))

This is repeated until no objects are detected anymore and no motion is active anymore

The result of this step are multiple snapshots that contains the captured objects with bounding boxes.

**Step 4**
When no objects are detected anymore and no motion is detected a new  timestamp is created, to mark the end of the detection.

**Step 5**
A mp4 named `latest_achtertuin.mp4` is created in the local media directory. This could be used, for example to notify your mobile phone with the MP4 as attachment. The event that will be generated by the service `imagedirectory.create_gif_mp4` after completion wil be used for this. See automation for creating a notification. In my case i only receive notifications when no one of my family is at home. When you want to use this example male sure you are enabled the mediasource integration.

This file could also be used in a generic camera for displaying the latest event.

**Step 6**
In my case i use the camera entity, so i need to update the camera with the latest images from the occuring events. I could have use the timestamps that are also use for creating the mp4 for mobile notification, but in my case i want a camera that shows me the last 2 hours of occuring events

```yaml
alias: Objectdetection achtertuin
description: ''
#STEP 1
trigger:
  - platform: state
    entity_id: input_boolean.motion_backyard
    from: 'off'
    to: 'on'
condition: []
#STEP 2
action:
  - variables:
      BeginTimeStamp: '{{now().strftime("%d/%m/%Y %H:%M:%S")}}'
  #STEP 3
  - repeat:
      while:
        - condition: or
          conditions:
            - condition: state
              entity_id: input_boolean.motion_backyard
              state: 'on'
            - condition: state
              entity_id: input_boolean.object_achtertuin_detected
              state: 'on'
      sequence:
        - service: image_processing.scan
          data: {}
          entity_id: image_processing.deepstack_object_achtertuin
#STEP 4
- variables:
      EndTimeStamp: '{{now().strftime("%d/%m/%Y %H:%M:%S")}}'
#STEP 5
- service: imagedirectory.create_gif_mp4
    data:
      sourcepath: /config/snapshots/achtertuin
      destinationpath: /config/www
      format: mp4
      filename: latest_achtertuin
      exclude: deepstack_object_achtertuin_latest.jpg
      begintimestamp: '{{BeginTimeStamp}}'
      endtimestamp: '{{EndTimeStamp}}'
#STEP 6
- service: imagedirectory.camera_update_image_filelist
    data:
      entity_id: camera.achtertuin_motion
      sourcepath: /config/snapshots/achtertuin
      exclude: deepstack_object_achtertuin_latest.jpg
      lasthours: 2
mode: single

```
Automation for setting:   `input_boolean.object_achtertuin_detected`


```yaml
alias: Object detection signal achtertuin
description: ''
trigger:
  - platform: event
    event_type: deepstack.object_detected
    event_data:
      entity_id: image_processing.deepstack_object_achtertuin
condition: []
action:
  - service: input_boolean.turn_on
    data: {}
    entity_id: input_boolean.object_achtertuin_detected
  - delay: '00:00:07'
  - service: input_boolean.turn_off
    data: {}
    entity_id: input_boolean.object_achtertuin_detected
mode: restart
```
Automation for notify to mobile phone

```yaml
alias: Notify new detection achtertuin
description: ''
trigger:
  - platform: event
    event_type: snaptogif
    event_data:
      Type: create
      sourcepath: /config/snapshots/achtertuin
condition:
  - condition: state
    entity_id: group.gezin
    state: Away
action:
  - service: notify.mobile_app_tf_jodur
    data:
      message: Object detection achtertuin
      data:
        attachment:
          url: 'media/local/latest_achtertuin.mp4'
          content-type: MPEG4
          hide-thumbnail: false
mode: single

```

### Example 2: Script to archive snapshots from the past day to a mp4

This example shows an script to archive the created snaphots, that a made during the previous automation. I schedule this script for example at 00:05:00

**Step 1**
Create begintime and endtime for the imagedirectory services. With the variable `daysback` you can control from which day you want to archive the snapshots. In mycase i want to archive the previous day. The file that is created will have a date  in its filename included

**Step 2**
Create the MP4 

**Step 3**
Wait for the event that the MP4 creation has finished
When a timeout occured, exit the script. Make sure to set the timeout long enoug in case you have many snapshot files. The creation of the MP4 could take some time

**Step 4**
Clear the image list from the current camera that is using the files

**Step 5**
Delete the snapshots you used to create the MP4

```yaml
alias: Create MP4 from snapshots achtertuin previous day
#STEP 1
sequence:
  - variables:
      daysback: 1
      begintime: '{{(now()-timedelta(days=daysback)).strftime("%d/%m/%Y")}} 00:00:00'
      endtime: '{{(now()-timedelta(days=daysback)).strftime("%d/%m/%Y")}} 23:59:59'
      fname: >-
        snapshots_achtertuin_{{(now()-timedelta(days=daysback)).strftime("%Y_%m_%d")}}
#STEP 2
  - service: imagedirectory.create_gif_mp4
    data:
      sourcepath: /config/snapshots/achtertuin
      destinationpath: /config/archive/achtertuin
      filename: '{{fname}}'
      format: mp4
      exclude: deepstack_object_achtertuin_latest.jpg
      begintimestamp: '{{begintime}}'
      endtimestamp: '{{endtime}}'
#STEP 3
- wait_for_trigger:
      - platform: event
        event_type: imagedirectory
        event_data:
          type: create_gif_mp4
          destinationpath: /config/archive/achtertuin
    timeout: '00:03:00'
    continue_on_timeout: false
 #STEP 4
 - service: imagedirectory.camera_clear_image_filelist
    data:
      entity_id: camera.achtertuin_motion
 #STEP 5
 - service: imagedirectory.delete_files
    data:
      sourcepath: /config/snapshots/achtertuin
      excludelist: deepstack_object_achtertuin_latest.jpg
      endtimestamp: '{{endtime}}'
mode: single

```

