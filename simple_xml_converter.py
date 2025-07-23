#!/usr/bin/env python3
"""
Simple XML to GCP Converter
A streamlined script to convert Agisoft Metashape marker export XML to GCP text format.
Now with GUI for easy use!
"""

import xml.etree.ElementTree as ET
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

try:
    from pyproj import CRS
    PYPROJ_AVAILABLE = True
except ImportError:
    PYPROJ_AVAILABLE = False
    print("Warning: pyproj not available. Install with: pip install pyproj")

def get_projection_string(epsg_code=None):
    """Get projection string from EPSG code with proper transformation parameters."""
    # Default projection string for RD New (EPSG:28992)
    default_projection = "+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs"
    
    if epsg_code is None:
        return default_projection, "28992"
    
    if not PYPROJ_AVAILABLE:
        print(f"Warning: Cannot convert EPSG:{epsg_code} - pyproj not installed. Using default projection.")
        return default_projection, "28992"
    
    try:
        # Create CRS from EPSG code
        crs = CRS.from_epsg(epsg_code)
        
        # Use legacy PROJ4 compatibility mode to get full string with all parameters
        # Mode 4 forces PROJ4 compatibility and includes all original parameters
        proj_string = crs.to_proj4(4)
        
        print(f"Successfully converted EPSG:{epsg_code} using legacy PROJ4 mode")
        return proj_string, str(epsg_code)
            
    except Exception as e:
        print(f"Warning: Could not convert EPSG:{epsg_code} - {e}. Using default projection.")
        return default_projection, "28992"

def convert_xml_to_gcp(xml_file, output_file=None, epsg_code=None):
    """Convert XML marker file to GCP text format."""
    
    if output_file is None:
        output_file = xml_file.replace('.xml', '_converted.txt')
    
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Get projection string from EPSG code or use default
    projection, used_epsg = get_projection_string(epsg_code)
    print(f"Using projection EPSG:{used_epsg}")
    print(f"Projection string: {projection}")
    
    # Get markers and their world coordinates
    markers = {}
    for marker in root.findall(".//markers/marker"):
        marker_id = marker.get('id')
        ref = marker.find('reference')
        if ref is not None:
            markers[marker_id] = {
                'x': float(ref.get('x', 0)),
                'y': float(ref.get('y', 0)),
                'z': float(ref.get('z', 0))
            }
    
    # Get camera names
    cameras = {}
    for camera in root.findall(".//cameras/camera"):
        camera_id = camera.get('id')
        label = camera.get('label', '')
        if label and not label.endswith('.JPG'):
            label += '.JPG'
        cameras[camera_id] = label
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{projection}\t\n")
        
        # Process marker projections
        for frame_marker in root.findall(".//frames/frame/markers/marker"):
            marker_id = frame_marker.get('marker_id')
            
            if marker_id in markers:
                marker = markers[marker_id]
                
                for location in frame_marker.findall('location'):
                    camera_id = location.get('camera_id')
                    if camera_id in cameras:
                        x_pixel = float(location.get('x', 0))
                        y_pixel = float(location.get('y', 0))
                        image_name = cameras[camera_id]
                        
                        f.write(f"{marker['x']:.9f}\t{marker['y']:.9f}\t{marker['z']:.9f}\t"
                               f"{x_pixel:.6f}\t{y_pixel:.6f}\t{image_name}\n")
    
    print(f"Conversion complete: {output_file}")
    return output_file

class XMLConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML to GCP Converter")
        self.root.geometry("600x400")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.epsg_code = tk.StringVar(value="28992")  # Default EPSG code
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="XML to GCP Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input file selection
        ttk.Label(main_frame, text="Input XML File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="Browse...", command=self.browse_input_file).grid(row=1, column=2, padx=(5, 0))
        
        # Output file selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(main_frame, text="Browse...", command=self.browse_output_file).grid(row=2, column=2, padx=(5, 0))
        
        # EPSG code input
        epsg_frame = ttk.Frame(main_frame)
        epsg_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(epsg_frame, text="EPSG Code:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        epsg_entry = ttk.Entry(epsg_frame, textvariable=self.epsg_code, width=10)
        epsg_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(epsg_frame, text="(e.g., 28992 for RD New, 4326 for WGS84)", 
                 font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W)
        
        # Test projection button
        ttk.Button(epsg_frame, text="Test Projection", 
                  command=self.test_projection).grid(row=0, column=3, padx=(10, 0))
        
        # Convert button
        convert_btn = ttk.Button(main_frame, text="Convert XML to GCP", 
                                command=self.convert_file, style="Accent.TButton")
        convert_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Status/log area
        ttk.Label(main_frame, text="Status:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = tk.Text(main_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S), pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Auto-detect XML files in current directory
        self.auto_detect_files()
        
    def auto_detect_files(self):
        """Automatically detect XML files in the current directory."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            xml_files = [f for f in os.listdir(current_dir) if f.endswith('.xml')]
            
            if xml_files:
                # Use the first XML file found
                xml_file_path = os.path.join(current_dir, xml_files[0])
                self.input_file.set(xml_file_path)
                
                # Set default output file
                output_path = xml_file_path.replace('.xml', '_converted.txt')
                self.output_file.set(output_path)
                
                self.log_message(f"Auto-detected XML file: {xml_files[0]}")
                if len(xml_files) > 1:
                    self.log_message(f"Found {len(xml_files)} XML files. Using: {xml_files[0]}")
            else:
                self.log_message("No XML files found in current directory. Please browse for a file.")
        except Exception as e:
            self.log_message(f"Error auto-detecting files: {e}")
    
    def browse_input_file(self):
        """Browse for input XML file."""
        filename = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-set output file
            output_path = filename.replace('.xml', '_converted.txt')
            self.output_file.set(output_path)
            self.log_message(f"Selected input file: {os.path.basename(filename)}")
    
    def browse_output_file(self):
        """Browse for output file location."""
        filename = filedialog.asksaveasfilename(
            title="Save GCP File As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            self.log_message(f"Set output file: {os.path.basename(filename)}")
    
    def test_projection(self):
        """Test the entered EPSG code and show the projection string."""
        try:
            # Test EPSG code
            epsg_code = int(self.epsg_code.get()) if self.epsg_code.get() else None
            projection, used_epsg = get_projection_string(epsg_code)
            
            self.log_message(f"Testing EPSG:{used_epsg}")
            self.log_message(f"Projection: {projection}")
            
            # Show in popup as well
            messagebox.showinfo(
                "Projection Test",
                f"EPSG:{used_epsg}\n\nProjection string:\n{projection}"
            )
            
        except ValueError:
            error_msg = "Please enter a valid EPSG code (numbers only)"
            self.log_message(f"Error: {error_msg}")
            messagebox.showerror("Invalid EPSG Code", error_msg)
        except Exception as e:
            error_msg = f"Error testing projection: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def log_message(self, message):
        """Add message to log area."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def convert_file(self):
        """Convert the XML file in a separate thread."""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input XML file")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        # Start conversion in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self._convert_worker)
        thread.daemon = True
        thread.start()
    
    def _convert_worker(self):
        """Worker function for conversion."""
        try:
            self.progress.start()
            self.log_message("Starting conversion...")
            
            # Get EPSG code
            try:
                epsg_code = int(self.epsg_code.get()) if self.epsg_code.get() else None
            except ValueError:
                epsg_code = None
                self.log_message("Warning: Invalid EPSG code, using default projection")
            
            # Call the conversion function
            output_file = convert_xml_to_gcp(
                self.input_file.get(), 
                self.output_file.get(), 
                epsg_code
            )
            
            self.progress.stop()
            self.log_message(f"✓ Conversion completed successfully!")
            self.log_message(f"Output saved to: {output_file}")
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Conversion completed!\n\nOutput file:\n{output_file}"
            ))
            
        except Exception as e:
            self.progress.stop()
            error_msg = f"✗ Error during conversion: {str(e)}"
            self.log_message(error_msg)
            
            # Show error message
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

def run_gui():
    """Run the GUI application."""
    root = tk.Tk()
    app = XMLConverterGUI(root)
    root.mainloop()

# Simple usage
if __name__ == "__main__":
    # Check if we should run GUI or command line
    if len(sys.argv) == 1:
        # No arguments - run GUI
        try:
            run_gui()
        except ImportError:
            print("GUI not available. Running in command line mode...")
            # Fallback to command line mode
            xml_files = [f for f in os.listdir('.') if f.endswith('.xml')]
            if xml_files:
                print(f"Found XML files: {xml_files}")
                xml_file = xml_files[0]
                print(f"Converting: {xml_file}")
                convert_xml_to_gcp(xml_file)
            else:
                print("Usage: python simple_converter.py input.xml [output.txt] [epsg_code]")
                print("Or place this script in a folder with XML files.")
                print("Examples:")
                print("  python simple_converter.py markers.xml")
                print("  python simple_converter.py markers.xml output.txt 4326")
                sys.exit(1)
    else:
        # Command line arguments provided - use original CLI mode
        xml_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        epsg_code = None
        
        # Check if EPSG code is provided as third argument
        if len(sys.argv) > 3:
            try:
                epsg_code = int(sys.argv[3])
                print(f"Using EPSG code: {epsg_code}")
            except ValueError:
                print(f"Warning: Invalid EPSG code '{sys.argv[3]}', using default projection")
        
        try:
            convert_xml_to_gcp(xml_file, output_file, epsg_code)
        except Exception as e:
            print(f"Error: {e}")
