import xml.etree.ElementTree as ET
import requests
import os

# Configuración del usuario y servidor
TRACCAR_URL = "https://traccar.mydomain/api"  # Cambia según tu servidor
EMAIL = "joedoe@gmail.com"  # Tu email de Traccar
PASSWORD = "mypassword"  # Tu contraseña de Traccar
KML_FILE_PATH = "mygeo.kml"  # Ruta del archivo KML

# Autenticación en Traccar
def authenticate():
    session = requests.Session()
    auth_url = f"{TRACCAR_URL}/session"
    auth_data = {"email": EMAIL, "password": PASSWORD}
    response = session.post(auth_url, data=auth_data, verify=False)
    if response.status_code == 200:
        print("Autenticación exitosa.")
        return session
    else:
        print("Error de autenticación:", response.status_code, response.text)
        return None

def parse_kml_to_wkt(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    wkt_geofences = []

    print("Analizando archivo KML...")

    def find_child_by_tag_ending(parent, tag_ending):
        """Find child element where tag ends with specified string"""
        for child in parent:
            if child.tag.endswith(tag_ending):
                return child
            # Also check nested children
            result = find_child_by_tag_ending(child, tag_ending)
            if result is not None:
                return result
        return None

    # Try to find placemarks with and without namespace
    placemarks = root.findall(".//kml:Placemark", ns)
    if not placemarks:
        # Try without namespace
        placemarks = []
        def find_placemarks(element):
            if element.tag.endswith('Placemark'):
                placemarks.append(element)
            for child in element:
                find_placemarks(child)
        find_placemarks(root)

    print(f"Found {len(placemarks)} placemarks")

    for placemark in placemarks:
        name_elem = placemark.find(".//kml:name", ns)
        if name_elem is None:
            # Try without namespace
            name_elem = find_child_by_tag_ending(placemark, "name")
        name = name_elem.text if name_elem is not None else "Geofence"

        description_elem = placemark.find(".//kml:Snippet", ns)
        if description_elem is None:
            description_elem = placemark.find(".//kml:description", ns)
            if description_elem is None:
                # Try without namespace
                description_elem = find_child_by_tag_ending(placemark, "description")
        description = description_elem.text if description_elem is not None else ""

        # Buscar diferentes tipos de geometría usando función auxiliar
        coords = None
        geometry_type = "POLYGON"

        # Buscar Polygon
        polygon = find_child_by_tag_ending(placemark, "Polygon")
        if polygon is not None:
            coords = find_child_by_tag_ending(polygon, "coordinates")
            geometry_type = "POLYGON"
        else:
            # Buscar LineString
            linestring = find_child_by_tag_ending(placemark, "LineString")
            if linestring is not None:
                coords = find_child_by_tag_ending(linestring, "coordinates")
                geometry_type = "LINESTRING"
            else:
                # Buscar Point
                point = find_child_by_tag_ending(placemark, "Point")
                if point is not None:
                    coords = find_child_by_tag_ending(point, "coordinates")
                    geometry_type = "POINT"

        if coords is not None and coords.text:
            coord_text = coords.text.strip()
            print(f"\nProcesando '{name}' ({geometry_type}):")
            print(f"Coordenadas raw: {coord_text[:200]}...")

            # Parse coordinates the same way as the working GPX converter
            points = []

            # Clean and split coordinates - handle both comma and space separated
            if ',' in coord_text:
                # KML format: lat,lon,alt lat,lon,alt or lat,lon lat,lon
                coord_text = coord_text.replace('\n', ' ').replace('\t', ' ')
                coordinate_points = [point.strip() for point in coord_text.split() if point.strip()]

                for point in coordinate_points:
                    if ',' in point:
                        coord_parts = point.split(',')
                        if len(coord_parts) >= 2:
                            try:
                                lat = float(coord_parts[0])
                                lon = float(coord_parts[1])
                                points.append((lon, lat))
                            except ValueError as e:
                                print(f"⚠ Error parseando coordenada '{point}': {e}")
            else:
                # Alternative format: space separated lat lon alt lat lon alt
                coord_text = coord_text.replace('\n', ' ').replace('\t', ' ').replace(',', ' ')
                coord_parts = coord_text.split()

                # Group coordinates (expecting lat, lon, [alt])
                i = 0
                while i < len(coord_parts):
                    try:
                        lat = float(coord_parts[i])
                        if i + 1 < len(coord_parts):
                            lon = float(coord_parts[i + 1])
                            points.append((lon, lat))
                            # Skip altitude if present
                            if i + 2 < len(coord_parts):
                                try:
                                    float(coord_parts[i + 2])  # Try to parse as altitude
                                    i += 3  # Skip lat, lon, alt
                                except ValueError:
                                    i += 2  # Skip only lat, lon
                            else:
                                i += 2
                        else:
                            break
                    except ValueError:
                        i += 1
                        continue

            print(f"Parsed {len(points)} coordinate points")

            if points:
                # Validar que las coordenadas estén en rangos válidos
                valid_points = []
                for lon, lat in points:
                    if -180 <= lon <= 180 and -90 <= lat <= 90:
                        valid_points.append((lon, lat))
                    else:
                        print(f"⚠ Coordenada inválida ignorada: lon={lon}, lat={lat}")

                if not valid_points:
                    print(f"⚠ Saltando '{name}' - no hay coordenadas válidas")
                    continue

                points = valid_points

                # Mostrar las coordenadas para debug
                print(f"Coordenadas para '{name}': {points[:3]}{'...' if len(points) > 3 else ''}")

                if geometry_type == "POLYGON":
                    # Para polígonos, asegurar que el primer y último punto sean iguales
                    if points[0] != points[-1]:
                        points.append(points[0])

                    # Formatear como WKT POLYGON (lon lat format)
                    wkt_points = ", ".join([f"{lon} {lat}" for lon, lat in points])
                    wkt = f"POLYGON(({wkt_points}))"

                elif geometry_type == "LINESTRING":
                    # Convertir LineString a Polygon si tiene suficientes puntos
                    if len(points) >= 3:
                        # Cerrar el polígono si no está cerrado
                        if points[0] != points[-1]:
                            points.append(points[0])
                        wkt_points = ", ".join([f"{lon} {lat}" for lon, lat in points])
                        wkt = f"POLYGON(({wkt_points}))"
                        print(f"Convertido LineString a Polygon: {name}")
                    else:
                        print(f"⚠ Saltando LineString '{name}' - necesita al menos 3 puntos para crear polígono")
                        continue

                elif geometry_type == "POINT":
                    # Convertir Point a un pequeño círculo (polígono octagonal)
                    lon, lat = points[0]
                    print(f"Creando polígono circular en: lon={lon}, lat={lat}")

                    # Crear un octágono pequeño alrededor del punto (radio aprox 100m)
                    # Ajustar el radio según la latitud para mantener forma circular
                    import math
                    radius_lat = 0.001  # Aproximadamente 100 metros en latitud
                    radius_lon = radius_lat / math.cos(math.radians(lat))  # Ajustar por latitud

                    octagon_points = []
                    for i in range(8):
                        angle = 2 * math.pi * i / 8
                        point_lon = lon + radius_lon * math.cos(angle)
                        point_lat = lat + radius_lat * math.sin(angle)
                        octagon_points.append((point_lon, point_lat))

                    # Cerrar el polígono
                    octagon_points.append(octagon_points[0])

                    wkt_points = ", ".join([f"{lon} {lat}" for lon, lat in octagon_points])
                    wkt = f"POLYGON(({wkt_points}))"
                    print(f"Convertido Point a Polygon circular: {name}")

                # Verificar que el WKT sea válido
                if "POLYGON" in wkt and len(points) >= 3:
                    wkt_geofences.append({
                        "name": name,
                        "description": description,
                        "area": wkt
                    })
                    print(f"✓ Procesada geocerca: {name} - {geometry_type} -> POLYGON")
                    print(f"  Coordenadas: {len(points)} puntos")
                    print(f"  Rango: lon {min(p[0] for p in points):.6f} a {max(p[0] for p in points):.6f}")
                    print(f"         lat {min(p[1] for p in points):.6f} a {max(p[1] for p in points):.6f}")
                else:
                    print(f"⚠ WKT inválido para '{name}': {wkt[:50]}...")

    return wkt_geofences

# Crear geocercas en Traccar
def create_geofences(session, geofences):
    geofence_url = f"{TRACCAR_URL}/geofences"
    for gf in geofences:
        payload = {
            "name": gf["name"],
            "description": gf["description"],
            "area": gf["area"]
        }
        
        print(f"Creando geocerca: {gf['name']}")
        print(f"Payload: {payload}")
        
        response = session.post(geofence_url, json=payload, verify=False)
        if response.status_code == 200:
            print(f"✓ Geocerca '{gf['name']}' creada exitosamente.")
        else:
            print(f"✗ Error al crear geocerca '{gf['name']}':")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            
            # Intentar obtener más detalles del error
            try:
                error_data = response.json()
                print(f"  Error details: {error_data}")
            except:
                pass

# Main
if __name__ == "__main__":
    if not os.path.exists(KML_FILE_PATH):
        print(f"El archivo KML no existe: {KML_FILE_PATH}")
        exit(1)
    
    session = authenticate()
    if session:
        geofences = parse_kml_to_wkt(KML_FILE_PATH)
        if geofences:
            print(f"Se encontraron {len(geofences)} geocercas para crear.")
            create_geofences(session, geofences)
        else:
            print("No se encontraron geocercas en el archivo KML.")
    else:
        print("No se pudo autenticar con Traccar.")
