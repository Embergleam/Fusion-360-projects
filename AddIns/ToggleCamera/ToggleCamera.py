"""
Fusion 360 Camera Toggle Add-in
Toggles between Perspective and Orthographic camera modes
"""

import adsk.core, traceback
import os

# Global variables
_app = None
_ui = None
_handlers = []

def run(context):
    """
    Basic run method that starts and configures the Add-In

    Args:
        context (dict[str, Any]): A dictionary of runtime parameters passed by 
                                  Fusion 360 when executing the Add-In
    """
    global _app, _ui
    try:
        # Get the application and the UI for this Add-In
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Get the path to the Add-In folder
        addinPath = os.path.dirname(os.path.realpath(__file__))
        orthoIconPath = os.path.join(addinPath, 'resources_orthographic')
        perspIconPath = os.path.join(addinPath, 'resources_perspective')
        
        # Create both command definitions and handlers for Orthographic ...
        cmdDefOrtho = _ui.commandDefinitions.itemById('CameraToggleOrtho')
        if not cmdDefOrtho:
            cmdDefOrtho = _ui.commandDefinitions.addButtonDefinition(
                'CameraToggleOrtho',
                'Switch to Orthographic',
                'Toggle between Perspective and Orthographic camera modes',
                orthoIconPath
            )
        # Connect to the command created event
        onCommandCreatedOrtho = CommandCreatedHandler()
        cmdDefOrtho.commandCreated.add(onCommandCreatedOrtho)
        _handlers.append(onCommandCreatedOrtho)
        
        # ... and Perspective
        cmdDefPersp = _ui.commandDefinitions.itemById('CameraTogglePersp')
        if not cmdDefPersp:
            cmdDefPersp = _ui.commandDefinitions.addButtonDefinition(
                'CameraTogglePersp',
                'Switch to Perspective',
                'Toggle between Perspective and Orthographic camera modes',
                perspIconPath
            )
        # Connect to the command created event
        onCommandCreatedPersp = CommandCreatedHandler()
        cmdDefPersp.commandCreated.add(onCommandCreatedPersp)
        _handlers.append(onCommandCreatedPersp)

        # Create the toolbar button
        try:
            createButtons(adsk.core.Application.get())
        except FusionNullObjectError as e:
            if _ui:
                _ui.messageBox(f'Fusion Error:\n{e}')
            else:
                print('Fusion Error:', e)
        except:
            # Button creation failed, try again using a WorkspaceActivatedHandler
            onWorkspaceActivated = WorkspaceActivatedHandler()
            _ui.workspaceActivated.add(onWorkspaceActivated)
            _handlers.append(onWorkspaceActivated)
        
    # Something went horribly wrong
    except:
        if _ui:
            _ui.messageBox('Failed in run():\n{}'.format(traceback.format_exc()))
        else:
            print('Failed in run():\n{}'.format(traceback.format_exc()))

def stop(context):
    """
    Basic stop method called when the Add-In is stopped or Fusion 360 exits

    Args:
        context (dict[str, Any]): A dictionary of runtime parameters passed by 
                                  Fusion 360 when stopping the Add-In
    """
    global _ui, _handlers
    try:
        if not _ui:
            _app = adsk.core.Application.get()
            _ui = _app.userInterface
        
        # Get the Solid tab and Inspect panel
        allToolbarTabs = _ui.allToolbarTabs
        solidTab = allToolbarTabs.itemById('SolidTab')
        if solidTab:
            inspectPanel = solidTab.toolbarPanels.itemById('InspectPanel')
            if inspectPanel:
                # Remove both possible buttons
                buttonControlOrtho = inspectPanel.controls.itemById('CameraToggleOrtho')
                if buttonControlOrtho:
                    buttonControlOrtho.deleteMe()
                    
                buttonControlPersp = inspectPanel.controls.itemById('CameraTogglePersp')
                if buttonControlPersp:
                    buttonControlPersp.deleteMe()
        
        # Remove both command definitions
        cmdDefOrtho = _ui.commandDefinitions.itemById('CameraToggleOrtho')
        if cmdDefOrtho:
            cmdDefOrtho.deleteMe()
            
        cmdDefPersp = _ui.commandDefinitions.itemById('CameraTogglePersp')
        if cmdDefPersp:
            cmdDefPersp.deleteMe()
        
        # Clear handlers
        _handlers.clear()
        
    # Something went horribly wrong
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createButtons(app):
    """
    Common method to create the buttons that this Add-In uses 

    Args:
        app (adsk.core.Application): The running Fusion 360 application instance 
    """
    global _ui
    
    # Get the viewport - this will throw as exception is the viewport is not available
    viewport = app.activeViewport
    currentCamera = viewport.camera

    # Find the Inspect panel under the SolidTab toolbar
    allToolbarTabs = _ui.allToolbarTabs
    solidTab = requiredNotNone(allToolbarTabs.itemById('SolidTab'), 'SOLID tab not found')
    if solidTab:
        inspectPanel = requiredNotNone(solidTab.toolbarPanels.itemById('InspectPanel'), 'INSPECT panel not found')
        if inspectPanel:
            # Delete any existing buttons
            toggleOrthoButton = inspectPanel.controls.itemById('CameraToggleOrtho')
            if toggleOrthoButton:
                toggleOrthoButton.deleteMe()
            togglePerspButton = inspectPanel.controls.itemById('CameraTogglePersp')
            if togglePerspButton:
                togglePerspButton.deleteMe()

            # Determine which button should be shown
            if currentCamera.cameraType == adsk.core.CameraTypes.PerspectiveCameraType:
                swapButtons('CameraTogglePersp', 'CameraToggleOrtho')
            else:
                swapButtons('CameraToggleOrtho', 'CameraTogglePersp')

def swapButtons(oldCmdId, newCmdId):
    """
    Method to change which button is shown when the camera mode is switched 

    Args:
        oldCmdId (String): The command identifier for the old button
        newCmdId (String): The command identifier for the new button
    """
    global _ui

    # Swap the button to show the opposite command
    allToolbarTabs = _ui.allToolbarTabs
    solidTab = requiredNotNone(allToolbarTabs.itemById('SolidTab'), 'SOLID tab not found')
    if solidTab:
        inspectPanel = requiredNotNone(solidTab.toolbarPanels.itemById('InspectPanel'), 'INSPECT panel not found')
        if inspectPanel:
            # Only swap if the old button exists and new button doesn't
            # button might already be correct if user changed mode externally
            oldButton = inspectPanel.controls.itemById(oldCmdId)
            newButton = inspectPanel.controls.itemById(newCmdId)

            # First check for the oldButton and delete it if necessary
            if oldButton:
                oldButton.deleteMe()

            # Is the required button missing
            if not newButton:
                # Create the new one linked to its command definition
                newCmdDef = requiredNotNone(_ui.commandDefinitions.itemById(newCmdId), f'No command definition for {newCmdId}')
                # Add the button to the Inspect panel
                newButton = inspectPanel.controls.addCommand(newCmdDef, newCmdId, False)
                # Make sure it is visible
                newButton.isPromoted = True
                newButton.isPromotedByDefault = True

class FusionApiError(Exception):
    """ Base class for Fusion API errors raised by our wrapper code. """

class FusionNullObjectError(FusionApiError):
    """ Raised when an API call returns None instead of an expected object. """

def requiredNotNone(obj, message='Unexpected None from Fusion API'):
    """
    Method to test if a provided object is not of type None 

    Args:
        obj (object): The object being tested
        message (str, optional): The message to use if the object fails the test
                                 Defaults to 'Unexpected None from Fusion API'
    Raises:
        FusionNullObjectError: Used when an object is found to be None
    Returns:
        object: The object that was tested
    """
    if obj is None:
        raise FusionNullObjectError(message)
    return obj

class WorkspaceActivatedHandler(adsk.core.WorkspaceEventHandler):
    """
    Handler that is called whenever the Workspace in Fusion 360 is Activated 

    Args:
        adsk (WorkspaceEventHandler): Abstract base class in the Fusion 360 API 
                                      that defines the interface for responding 
                                      to Workspace events
    """
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        """
        The method that is called when a Workspace Event happens

        Args:
            args (adsk.core.WorkspaceEventArgs): Information about the workspace that 
                                                 was activated or deactivated
        """
        # Update button based on current camera mode now that viewport is ready
        try:
            createButtons(adsk.core.Application.get())
        except FusionNullObjectError as e:
            # SOLID tab or INSPECT panel Objects we expected to find did not exist
            if _ui:
                _ui.messageBox(f'Fusion Error:\n{e}')
            else:
                print('Fusion Error:', e)
        except:
            # Something went horribly wrong
            if _ui:
                _ui.messageBox('Failed in WorkspaceActivatedHandler():\n{}'.format(traceback.format_exc()))
            else:
                print('Failed in WorkspaceActivatedHandler():\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """
    Handler that is called whenever to handle the CommandCreated event, which fires 
    whenever a new command definition is executed

    Args:
        adsk (CommandCreatedEventHandler): Abstract base class in the Fusion 360 API 
                                           that defines the interface for responding 
                                           to Command creation events
    """
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        """
        The method that is called when a Command Creation Event happens

        Args:
            args (adsk.core.CommandEventArgs): Provides access to .command 
                                               (the new command object)
        """
        # Create a new handler
        try:
            cmd = args.command
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            else:
                print('Failed:\n{}'.format(traceback.format_exc()))

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    """
    This is the class that does all the work for the Add-In 

    Args:
        adsk (CommandEventHandler): Abstract base class in the Fusion 360 API 
                                    that defines the interface for responding 
                                    to Command events
    """
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        """
        The method that is called when a Command Event happens
        This method checks which camera is currently being used and switches 
        to the other camera 

        Args:
            args (adsk.core.CommandEventArgs): Provides access to .command 
                                               (the new command object)
        """
        try:
            app = adsk.core.Application.get()
            viewport = app.activeViewport
            currentCamera = viewport.camera
            
            # CRITICAL: Always check current state before toggling
            # The user might have changed modes via Display Settings menu
            # Note: 'Perspective with Ortho Faces' will be treated as regular Perspective mode
            currentType = currentCamera.cameraType
            
            # Save current view info
            eye = currentCamera.eye
            target = currentCamera.target
            upVector = currentCamera.upVector
            
            # Toggle between perspective and orthographic based on CURRENT state
            if currentType == adsk.core.CameraTypes.PerspectiveCameraType:
                # Currently Perspective - Switching TO Orthographic
                import math
                
                # Get viewport aspect ratio
                viewportWidth = viewport.width
                viewportHeight = viewport.height
                aspectRatio = viewportWidth / viewportHeight if viewportHeight > 0 else 1.0
                
                # Calculate the vertical and horizontal sizes visible at the target distance
                verticalSize =  2.0 * eye.distanceTo(target) * math.tan(currentCamera.perspectiveAngle / 2.0)
                horizontalSize = verticalSize * aspectRatio
                
                # Change the current camera to an orthographic camera
                currentCamera.cameraType = adsk.core.CameraTypes.OrthographicCameraType
                currentCamera.isSmoothTransition = False
                
                # Assign the changed camera to the viewport
                viewport.camera = currentCamera

                # Get the new Camera and set it extents
                attachedCamera = viewport.camera
                attachedCamera.isSmoothTransition = False
                attachedCamera.setExtents(horizontalSize, verticalSize)

                # Assign the final camera to the viewport
                viewport.camera = attachedCamera

                # Swap the buttons
                swapButtons('CameraToggleOrtho', 'CameraTogglePersp')
                
            else:
                # Currently Orthographic - Switching TO Perspective
                import math
                
                # Get the current vertical size from the current camera's extents
                _, _, verticalSize = currentCamera.getExtents()

                # Change the current camera to a perspective camera
                currentCamera.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
                currentCamera.isSmoothTransition = False
                currentCamera.isFitView = True

                # Assign the changed camera to the viewport
                viewport.camera = currentCamera

                # Calculate distance needed for this vertical size
                desiredDistance = (verticalSize / 2.0) / math.tan(viewport.camera.perspectiveAngle / 2.0)
                
                # Calculate new eye position maintaining the same direction
                direction = eye.asVector()
                direction.subtract(target.asVector())
                direction.normalize()
                direction.scaleBy(desiredDistance)

                # Create a new eye                
                newEye = target.copy()
                newEye.translateBy(direction)

                # Get the new Camera and set it's new eye
                attachedCamera = viewport.camera
                attachedCamera.eye = newEye
                attachedCamera.target = target
                attachedCamera.upVector = upVector
                attachedCamera.isSmoothTransition = False

                # Assign the final camera to the viewport
                viewport.camera = attachedCamera
                
                # Swap the buttons
                swapButtons('CameraTogglePersp', 'CameraToggleOrtho')
            
            # Refresh the viewport to display the changed camera view
            viewport.refresh()

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))