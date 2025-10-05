# Camera Toggle Add-in for Fusion 360

A Fusion 360 add-in that provides quick toggling between Perspective and Orthographic camera modes while preserving zoom level and focus point.

## Features

- **Quick Toggle**: Switch between Perspective and Orthographic camera modes with a single click
- **Dynamic Button**: Button icon that shows the current camera mode and a text update to show the target mode when clicking the button
- **Keyboard Shortcut Support**: Assign a custom keyboard shortcut for even faster toggling

## Usage

### Basic Usage

1. The add-in adds a button to the **Inspect panel** in the **Solid tab**
2. Click the button to toggle between Perspective and Orthographic camera modes
3. The button icon will change to show what mode you are in currently
4. The buttom text will update to show which mode you'll switch to next if clocked

### Setting Up a Keyboard Shortcut

For maximum efficiency, assign a keyboard shortcut:

1. Hover over the "Switch to Orthographic" or "Switch to Perspective" button in the Inspect panel
2. Click the **three dots (...)** that appear on the right side of the button
3. Select **"Change Keyboard Shortcuts"**
4. Assign your preferred shortcut (recommended: **Shift+X**)

### Camera Modes

The add-in supports two camera modes:

- **Perspective**: Standard 3D perspective view with depth perception
- **Orthographic**: Parallel projection view (no perspective distortion)

**Note**: "Perspective with Ortho Faces" mode is treated as regular Perspective mode. This hybrid mode dynamically switches between orthographic and perspective based on view orientation, and the add-in will toggle whichever camera type is currently active.

## Technical Details

### How It Works

The add-in calculates the appropriate camera extents and positioning to maintain the same visible area when switching modes:

- **Perspective → Orthographic**: Calculates the field of view at the target distance and sets orthographic extents to match
- **Orthographic → Perspective**: Adjusts camera distance to maintain the same visible height based on the perspective angle

The calculations account for viewport aspect ratio to ensure consistent zoom across different window sizes.

### Known Limitations

- The button icon/text may not update immediately if you change camera modes using Fusion's **Display Settings → Camera** menu. However, the toggle will still work correctly as it always checks the current camera state before switching.
- "Perspective with Ortho Faces" mode cannot be reliably detected via the API and is treated as standard Perspective mode.

## Troubleshooting

**Button not appearing:**
- Verify the add-in is enabled in **Utilities → Add-Ins → Scripts and Add-Ins**
- Check that the Solid tab and Inspect panel exist in your workspace
- Ensure icon folders and files are properly named and located

**Toggle not working:**
- Make sure you're in either Perspective or Orthographic mode (not a named view)
- Check the Fusion 360 console for error messages

**Zoom not preserved correctly:**
- This is most noticeable when toggling from "Perspective with Ortho Faces" mode
- Switch to standard Perspective or Orthographic mode first for best results

## Contributing

Contributions are welcome! If you find bugs or have feature suggestions, please open an issue or submit a pull request.

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Credits

Developed for Autodesk Fusion 360 using the Fusion 360 API.

## Version History

- **1.0.0** - Initial release
  - Basic toggle functionality
  - Zoom and focus preservation
  - Dynamic button icons
  - Keyboard shortcut support
