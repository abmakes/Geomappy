from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim
from io import BytesIO
import xlsxwriter
import folium
import pandas as pd

#from werkzeug import secure_filename

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/csv_template")
def csv_template():
    return send_file('static/csv_template.csv', attachment_filename="csv_template.csv", as_attachment=True)
    
@app.route("/upload", methods=['GET', 'POST'])
def upload(): 
    if request.method=='POST':
        csvfile=request.files["file"]
        try:
            webtable=geocodecsv(csvfile)
            return render_template("table.html", data=webtable)
        except:
           return render_template("index.html", text="Please submit a CSV file with an 'Address' column!")

def make_dftable(file):
    return df

def geocodecsv(file):
    global df
    df=pd.read_csv(file) 

    #APPLY GEOCODING FUNCTION TO THE "Address" COLUMN AND SAVE IN TEMP COLUMN "coord"
    geolocator=Nominatim(user_agent="Geomappy1")
    df["coord"]=df["Address"].apply(geolocator.geocode)

    #EXTRACT LAT AND LONG TO THERE OWN COLUMNS
    df["LATITUDE"]=df["coord"].apply(lambda x: x.latitude)
    df["LONGITUDE"]=df["coord"].apply(lambda y: y.longitude)

    #REMOVE TEMP COLUMN "coord" AND EXPORT TO CSV
    df=df.drop(axis=1, columns="coord")
    
    #convert df in html to be adde as data in a HTML template
    webtable = df.to_html(index=False)
    return webtable

@app.route("/map")
def show_map():

    lat = list(df["LATITUDE"])
    lon = list(df["LONGITUDE"])
    name = list(df["Name"])
    value = list(df["Employees"])
  
    #Use the mid point between the two most outer points to center the map
    start_coords = [((max(lat)+min(lat))/2), ((max(lon)+min(lon))/2)]
    
    #Add a 50% padding to the outside of the points before stting the map bounds
    padlat = (max(lat)-min(lat))/2
    padlon = (max(lon)-min(lon))/2
    sw = ((min(lat)-padlat), (min(lon)-padlon))
    ne = ((max(lat)+padlat), (max(lon)+padlon))
    
    fmap = folium.Map(location=start_coords, zoom_start=6, tiles="Stamen Toner")
    
    points = folium.FeatureGroup(name="Points of Interest")

    for lt, ln, nam, val in zip(lat, lon, name, value):
        points.add_child(folium.CircleMarker(location=[lt, ln], radius=val, popup=nam, fill=True, fill_opacity=0.6))

    #Add points to check center and padding
    # points.add_child(folium.Marker(location=ne))
    # points.add_child(folium.Marker(location=sw))
    # points.add_child(folium.Marker(location=start_coords))

    fmap.add_child(points)
    fmap.fit_bounds([ne, sw])

    return fmap._repr_html_()

@app.route("/download")

def downloadFile():
    #Uses in memory storage(BytesIO) and XlsxWrite to create a xlsx file and send_file to output it to the user
    data = df
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    data.to_excel(writer, sheet_name="Sheet1", index=False)
    writer.save()
    output.seek(0)
    return send_file(output, attachment_filename="geomappy.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.debug=True
    app.run()
