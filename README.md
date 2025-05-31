# km_to_traccar2 - KML to Traccar Geofence Converter  
**Author:** Renzo Uribe  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  

---

## 📌 Description  
This Python script converts geofences defined in **KML (Keyhole Markup Language)** files into **Traccar-compatible geofences** using the [Traccar GPS Tracking API](https://www.traccar.org/api/). It parses KML data, converts geometries (points, linestrings, polygons) into Well-Known Text (WKT) format, and uploads them to a Traccar server.  

---

## 🛠️ Features  
- **KML Parsing**: Extracts geofence data from `.kml` files.  
- **Geometry Conversion**:  
  - Converts **Points** into circular polygons (approx. 100m radius).  
  - Converts **LineStrings** into closed polygons (requires ≥3 points).  
  - Supports **Polygons** directly.  
- **Traccar API Integration**:  
  - Authenticates with Traccar using email/password.  
  - Creates geofences via the `/geofences` endpoint.  
- **Error Handling**: Skips invalid coordinates or malformed KML data.  
- **Customizable**: Configurable Traccar server URL, credentials, and KML file path.  

---

## 📥 Requirements  
- **Python 3.x** (standard libraries only: `xml.etree.ElementTree`, `requests`, `os`).  
- A running **Traccar server** instance (e.g., [demo.traccar.org](https://demo.traccar.org/)).  
- A user account with **permission to create geofences**.  

---

## 📝 Configuration  
Edit the script's top section:  

```python
TRACCAR_URL = "http://your-traccar-server:port/api"  # e.g., http://traccar.mydomain.org:8082/api
EMAIL = "your-email@example.com"  # Traccar user email
PASSWORD = "your-password"  # Traccar user password
KML_FILE_PATH = "path/to/your/file.kml"  # e.g., "geo.kml"
```

---

## 🚀 Usage  
1. **Install Python 3** if not already installed.  
2. Save this script as `km_to_traccar2.py`.  
3. Run the script:  
   ```bash
   python km_to_traccar2.py
   ```  
4. **Monitor Output**: The script will print progress, errors, and success messages.  

---

## 🧱 How It Works  
1. **Authentication**: Logs into the Traccar server using provided credentials.  
2. **KML Parsing**:  
   - Extracts `Placemark` data (name, description, geometry).  
   - Converts geometries to WKT format (e.g., `POLYGON((lon1 lat1, lon2 lat2, ...))`).  
3. **Geofence Creation**:  
   - Posts WKT data to the Traccar API endpoint `/geofences`.  
   - Maps KML `name` and `description` to Traccar geofence properties.  

---

## 📌 License  
This project is licensed under the **Creative Commons Attribution 4.0 International License** ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).  

You are free to:  
- **Share** — copy and redistribute the material in any medium.  
- **Adapt** — remix, transform, and build upon the work.  

**Under the following terms**:  
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.  
- **Original Author**: Renzo Uribe.  

---

## 📌 Contributing  
- **Issues**: Report bugs or request features via GitHub issues.  
- **Pull Requests**: Welcome improvements or new features.  
- **Contact**: Reach out to the author at [renzo.uribe@example.com](mailto:renzo.uribe@example.com).  

---

## 📚 References  
- [Traccar API Documentation](https://www.traccar.org/api/)  
- [KML Format Specification](https://developers.google.com/kml/documentation/)  
- [CC BY 4.0 License](https://creativecommons.org/licenses/by/4.0/)  

---  
**Original Author**: Renzo Uribe  
**GitHub**: [https://github.com/ruribe17/traccar-exporting-tools/tree/main]([https://github.com/ruribe17/traccar-exporting-tools/tree/main])
