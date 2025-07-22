# XML to GCP Converter

A simple tool to convert Agisoft Metashape marker export XML files to GCP (Ground Control Point) text format for OpenDroneMap.

## Features

- **GUI Interface**: Easy-to-use graphical interface
- **Command Line Support**: Batch processing and automation
- **EPSG Code Support**: Automatic coordinate system conversion
- **Auto-Detection**: Automatically finds XML files in the current directory
- **Default Projection**: Uses RD New (EPSG:4326) as default

## Installation

### Prerequisites
- Python 3.x
- tkinter (usually included with Python)

### Optional Dependencies
For EPSG code conversion support:
```bash
pip install pyproj
```

Or run the provided installer:
```bash
install_pyproj.bat
```

## Usage

### GUI Mode (Recommended)

1. **Run the converter**:
   ```bash
   python simple_xml_converter.py
   ```
   Or double-click:
   ```bash
   run_converter.bat
   ```

2. **Using the interface**:
   - **Input XML File**: Browse or auto-detected from current directory
   - **Output File**: Automatically set or browse to choose location
   - **EPSG Code**: Enter coordinate system code (default: 4326 for WSG84)
   - **Test Projection**: Verify your EPSG code before conversion
   - **Convert**: Process the XML file

### Command Line Mode

```bash
# Basic conversion (uses default projection)
python simple_xml_converter.py input.xml

# Specify output file
python simple_xml_converter.py input.xml output.txt

# Use specific EPSG code
python simple_xml_converter.py input.xml output.txt 4326
```

## Supported EPSG Codes

Common coordinate systems:
- **4326**: WGS84 (Global GPS coordinates)
- **3857**: Web Mercator
- **32631**: UTM Zone 31N
- **25831**: ETRS89 UTM Zone 31N

⚠️ **Important Warning**: EPSG code conversion doesn't always work correctly with all coordinate systems. The converted PROJ4 string may not include all necessary transformation parameters (especially datum shifts). **Always verify the resulting projection string** using the "Test Projection" button before converting your data. For critical applications, manually specify the complete PROJ4 string instead of relying solely on EPSG codes.

## Input Format

The tool expects XML files exported from Agisoft Metashape containing:
- Marker coordinates (world coordinates)
- Camera information
- Marker projections in images

## Output Format

The output is a tab-separated text file with:
```
[PROJ4_STRING]
X_world  Y_world  Z_world  X_pixel  Y_pixel  Image_name.JPG
```

Example:
```
+proj=longlat +datum=WGS84 +no_defs	
-74.123456  40.789012  10.123456789  1024.25  768.50  IMG_001.JPG
```

## File Structure

```
xml-converter/
├── simple_xml_converter.py    # Main converter script
├── install_pyproj.bat         # Install dependencies
├── run_converter.bat          # Run GUI converter
└── README.md                  # This guide
```

## Troubleshooting

### "pyproj not available" Warning
- click on install_pyproj.bat
- Install pyproj: `pip install pyproj`
- Or use the default WGS84 projection

### "No XML files found"
- Place XML files in the same directory as the script
- Or use the Browse button to select files manually

### Invalid EPSG Code
- Use the "Test Projection" button to verify codes
- Check [epsg.io](https://epsg.io) for valid EPSG codes
- Leave empty to use default WGS84 projection

### GUI Not Starting
- Ensure tkinter is installed with Python
- The script will automatically fall back to command line mode

## Example Workflow

1. Export markers from Agisoft Metashape as XML
2. Place the XML file in the converter directory
3. Run `run_converter.bat`
4. Adjust EPSG code if needed (default: 4326)
5. **Test the projection** to verify the PROJ4 string is correct
6. Click "Convert XML to GCP"
7. Use the generated text file in your photogrammetry software

## Notes

- The tool automatically adds `.JPG` extension to image names if missing
- World coordinates are preserved with high precision (9 decimal places for Z)
- The GUI shows conversion progress and detailed logs
- Multiple XML files in directory: first one is auto-selected
- **Critical**: Always verify the projection string output, especially for datum transformations
- EPSG-to-PROJ4 conversion may omit important transformation parameters

## Support

For issues or questions about coordinate systems, refer to:
- [EPSG.io](https://epsg.io) - EPSG code database
- [PROJ documentation](https://proj.org) - Projection information
